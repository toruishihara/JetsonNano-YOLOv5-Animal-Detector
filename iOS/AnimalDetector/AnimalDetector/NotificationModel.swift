//
//  NotificationModel.swift
//  AnimalDetector
//
//  Created by Toru Ishihara on 2026/05/29.
//

import Foundation
import Combine

class NotificationModel: ObservableObject {
    static let shared = NotificationModel()

    @Published var title: String = "No message"
    @Published var body: String = ""
    @Published var fcmToken: String = ""

    @Published var history: [AlertItem] = []

    private init() {}

    func addNotification(title: String, body: String) {
        let item = AlertItem(
            title: title,
            body: body,
            date: Date(timeIntervalSince1970: 0)
        )

        history.insert(item, at: 0)

        self.title = title
        self.body = body

        // Keep only last 12 hours
        //let twelveHoursAgo = Date().addingTimeInterval(-12 * 60 * 60)
        //history = history.filter { $0.date >= twelveHoursAgo }
    }
}
