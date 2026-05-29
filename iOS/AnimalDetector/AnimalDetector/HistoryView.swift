//
//  HistoryView.swift
//  AnimalDetector
//
//  Created by Toru Ishihara on 2026/05/29.
//


import SwiftUI

struct HistoryView: View {
    var body: some View {
        NavigationView {
            VStack {
                Text("Last 12 Hours")
                    .font(.title)

                Text("Show Firebase alert history here")
                    .foregroundColor(.secondary)
            }
            .navigationTitle("History")
        }
    }
}