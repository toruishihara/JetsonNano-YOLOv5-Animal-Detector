//
//  FirebaseHistoryService.swift
//  AnimalDetector
//
//  Created by Toru Ishihara on 2026/05/29.
//


import Foundation
import FirebaseDatabase

class FirebaseHistoryService {
    static func loadLast24Hours(completion: @escaping ([AlertItem]) -> Void) {
        _ = Int64(
            Date().addingTimeInterval(-24 * 60 * 60).timeIntervalSince1970 * 1000
        )
        
        let ref = Database.database().reference()
        
        ref.child("alerts")
            .queryOrdered(byChild: "timestamp")
        //.queryStarting(atValue: twelveHoursAgo)
            .observeSingleEvent(of: .value) { snapshot, _ in
                
                var items: [AlertItem] = []
                
                for child in snapshot.children {
                    guard let snap = child as? DataSnapshot else {
                        continue
                    }
                    
                    guard let dict = snap.value as? [String: Any] else {
                        continue
                    }
                    
                    let title = dict["title"] as? String ?? "Animal Alert"
                    let message = dict["message"] as? String ?? ""
                    let timeString = dict["time"] as? String ?? ""
                    let dateItem = parseFirebaseTime(timeString) ?? Date(timeIntervalSince1970: 0)
                    let item = AlertItem(
                        title: title,
                        body: message,
                        date: dateItem
                    )
                    items.append(item)
                }
                
                let sortedItems = items.sorted {
                    $0.date > $1.date
                }
                
                DispatchQueue.main.async {
                    completion(sortedItems)
                }
            }
    }
    
    static func parseFirebaseTime(_ timeString: String) -> Date? {
        let formatterWithFraction = ISO8601DateFormatter()
        formatterWithFraction.formatOptions = [
            .withInternetDateTime,
            .withFractionalSeconds
        ]
        
        if let date = formatterWithFraction.date(from: timeString) {
            return date
        }
        
        let formatterWithoutFraction = ISO8601DateFormatter()
        formatterWithoutFraction.formatOptions = [
            .withInternetDateTime
        ]
        
        return formatterWithoutFraction.date(from: timeString)
    }
}
