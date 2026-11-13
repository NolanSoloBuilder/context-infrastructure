import Foundation
import AVFoundation
let path = CommandLine.arguments[1]
let asset = AVURLAsset(url: URL(fileURLWithPath: path))
Task {
    do {
        let group = try await asset.loadMediaSelectionGroup(for: .legible)
        let options = group?.options.map { option in
            ["displayName": option.displayName, "locale": option.locale?.identifier ?? "", "language": option.extendedLanguageTag ?? "", "playable": String(option.isPlayable)]
        } ?? []
        let data = try JSONSerialization.data(withJSONObject: ["subtitle_options": options], options: [.prettyPrinted, .sortedKeys])
        print(String(data: data, encoding: .utf8)!)
        exit(options.isEmpty ? 1 : 0)
    } catch { print(error); exit(2) }
}
RunLoop.main.run()
