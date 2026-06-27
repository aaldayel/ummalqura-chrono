// swift-tools-version: 5.9
// SPDX-License-Identifier: MIT
import PackageDescription

let package = Package(
    name: "UmmAlQura",
    products: [
        .library(name: "UmmAlQura", targets: ["UmmAlQura"]),
    ],
    targets: [
        .target(
            name: "UmmAlQura",
            resources: [
                .copy("../../../../data/ummalqura-months.json")
            ]
        ),
        .testTarget(
            name: "UmmAlQuraTests",
            dependencies: ["UmmAlQura"]
        ),
    ]
)
