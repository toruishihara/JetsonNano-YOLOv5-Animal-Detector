//
//  AlertItem.swift
//  AnimalDetector
//
//  Created by Toru Ishihara on 2026/05/29.
//


import Foundation

struct AlertItem: Identifiable {
    let id = UUID()
    let title: String
    let body: String
    let date: Date
}
