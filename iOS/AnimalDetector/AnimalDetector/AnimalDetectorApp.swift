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
    
    @StateObject private var notificationModel = NotificationModel.shared

    var body: some Scene {
        WindowGroup {
            MainTabView()
                .environmentObject(notificationModel)
        }
    }
}
