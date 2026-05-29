//
//  HistoryView.swift
//  AnimalDetector
//
//  Created by Toru Ishihara on 2026/05/29.
//


import SwiftUI

import SwiftUI

struct HistoryView: View {
    @EnvironmentObject var notificationModel: NotificationModel
    @State private var lastUpdatedText = "Not loaded yet"

    var body: some View {
        NavigationView {
            VStack {
                Text("Last updated: \(lastUpdatedText)")
                    .font(.caption)
                    .foregroundColor(.secondary)
                List {
                    if notificationModel.history.isEmpty {
                        Text("No notifications in last 12 hours")
                            .foregroundColor(.secondary)
                    } else {
                        ForEach(notificationModel.history) { item in
                            VStack(alignment: .leading, spacing: 6) {
                                Text(item.title)
                                    .font(.headline)
                                
                                Text(item.body)
                                    .font(.body)
                                
                                Text(item.date.formatted(date: .abbreviated, time: .standard))
                                    .font(.caption)
                                    .foregroundColor(.secondary)
                            }
                            .padding(.vertical, 4)
                        }
                    }
                }
            }
            .navigationTitle("History")
            .toolbar {
                Button("Refresh") {
                    loadHistory()
                }
            }
            .onAppear {
                loadHistory()
            }
        }
    }
    
    private func loadHistory() {
        FirebaseHistoryService.loadLast24Hours { items in
            DispatchQueue.main.async {
                notificationModel.history = items
                lastUpdatedText = Date().formatted(date: .omitted, time: .standard)
            }
        }
    }
}
