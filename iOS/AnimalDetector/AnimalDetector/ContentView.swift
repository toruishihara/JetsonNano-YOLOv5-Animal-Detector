//
//  ContentView.swift
//  AnimalDetector
//
//  Created by Toru Ishihara on 2026/05/29.
//


import SwiftUI

struct ContentView: View {
    @EnvironmentObject var notificationModel: NotificationModel

    var body: some View {
        VStack(spacing: 20) {
            Text("Animal Detector")
                .font(.title)

            VStack(alignment: .leading, spacing: 8) {
                Text("Last notification")
                    .font(.headline)

                Text(notificationModel.title)
                    .font(.title2)

                Text(notificationModel.body)
                    .font(.body)
            }

            VStack(alignment: .leading, spacing: 8) {
                Text("FCM token")
                    .font(.headline)

                Text(notificationModel.fcmToken)
                    .font(.caption)
                    .textSelection(.enabled)
                    .lineLimit(6)
            }
        }
        .padding()
    }
}
