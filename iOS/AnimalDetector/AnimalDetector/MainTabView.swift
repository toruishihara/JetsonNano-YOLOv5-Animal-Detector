//
//  MainTabView.swift
//  AnimalDetector
//
//  Created by Toru Ishihara on 2026/05/29.
//


import SwiftUI

struct MainTabView: View {
    var body: some View {
        TabView {
            CurrentView()
                .tabItem {
                    Image(systemName: "dot.radiowaves.left.and.right")
                    Text("Current")
                }

            HistoryView()
                .tabItem {
                    Image(systemName: "clock.arrow.circlepath")
                    Text("History")
                }

            LicenseView()
                .tabItem {
                    Image(systemName: "doc.text")
                    Text("License")
                }
        }
    }
}