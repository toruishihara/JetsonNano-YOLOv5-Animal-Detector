//
//  LicenseView.swift
//  AnimalDetector
//
//  Created by Toru Ishihara on 2026/05/29.
//


import SwiftUI

struct LicenseView: View {
    var body: some View {
        NavigationView {
            ScrollView {
                Text("""
                Animal Detector

                License information will be shown here.

                Firebase
                Swift
                YOLOv5n
                Jetson Nano
                """)
                .padding()
            }
            .navigationTitle("License")
        }
    }
}
