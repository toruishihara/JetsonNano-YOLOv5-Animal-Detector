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

    @Published var title: String = "No notification yet"
    @Published var body: String = ""
    @Published var fcmToken: String = ""
}