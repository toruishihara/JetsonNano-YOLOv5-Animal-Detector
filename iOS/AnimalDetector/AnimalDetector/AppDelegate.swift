//
//  AppDelegate.swift
//  AnimalDetector
//
//  Created by Toru Ishihara on 2026/05/29.
//


import UIKit
import FirebaseCore
import FirebaseMessaging
import UserNotifications

class AppDelegate: NSObject, UIApplicationDelegate, UNUserNotificationCenterDelegate, MessagingDelegate {

    func application(
        _ application: UIApplication,
        didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey : Any]? = nil
    ) -> Bool {

        FirebaseApp.configure()

        UNUserNotificationCenter.current().delegate = self
        Messaging.messaging().delegate = self

        UNUserNotificationCenter.current().requestAuthorization(options: [.alert, .sound, .badge]) { granted, error in
            print("notification permission:", granted)

            if let error = error {
                print("permission error:", error)
            }
        }

        application.registerForRemoteNotifications()

        return true
    }

    func application(
        _ application: UIApplication,
        didRegisterForRemoteNotificationsWithDeviceToken deviceToken: Data
    ) {
        print("APNs token received")
        Messaging.messaging().apnsToken = deviceToken
    }

    func messaging(
        _ messaging: Messaging,
        didReceiveRegistrationToken fcmToken: String?
    ) {
        guard let fcmToken = fcmToken else {
            print("FCM token is nil")
            return
        }

        print("FCM token:", fcmToken)

        DispatchQueue.main.async {
            NotificationModel.shared.fcmToken = fcmToken
        }
    }

    // When app is open
    func userNotificationCenter(
        _ center: UNUserNotificationCenter,
        willPresent notification: UNNotification,
        withCompletionHandler completionHandler: @escaping (UNNotificationPresentationOptions) -> Void
    ) {
        let content = notification.request.content

        DispatchQueue.main.async {
            NotificationModel.shared.title = content.title
            NotificationModel.shared.body = content.body
        }

        completionHandler([.banner, .sound, .badge])
    }

    // When user taps notification
    func userNotificationCenter(
        _ center: UNUserNotificationCenter,
        didReceive response: UNNotificationResponse,
        withCompletionHandler completionHandler: @escaping () -> Void
    ) {
        let content = response.notification.request.content

        DispatchQueue.main.async {
            NotificationModel.shared.title = content.title
            NotificationModel.shared.body = content.body
        }

        completionHandler()
    }
}