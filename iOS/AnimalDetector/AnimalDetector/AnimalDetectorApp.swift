//
//  AnimalDetectorApp.swift
//  AnimalDetector
//
//  Created by Toru Ishihara on 2026/05/29.
//

import SwiftUI

@main
struct AnimalDetectorApp: App {
    @UIApplicationDelegateAdaptor(AppDelegate.self) var appDelegate

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(NotificationModel.shared)
        }
    }
}
