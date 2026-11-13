import Foundation
let root = URL(fileURLWithPath: CommandLine.arguments[1]).standardizedFileURL
let keep = root.appendingPathComponent("anthropic_roadshow_bilingual.mp4")
let fm = FileManager.default
guard fm.fileExists(atPath: keep.path), fm.fileExists(atPath: root.appendingPathComponent("verification/xhs_compatible/visible_validation.json").path) else { fatalError("Verified replacement missing; cleanup aborted") }
let enumFiles = fm.enumerator(at: root, includingPropertiesForKeys: [.isRegularFileKey, .fileSizeKey])!
var files: [URL] = []
for case let file as URL in enumFiles {
    if ["mp4", "mov", "mkv", "webm", "m4v"].contains(file.pathExtension.lowercased()), file.standardizedFileURL != keep {
        files.append(file)
    }
}
var manifest: [[String: Any]] = []
for file in files.sorted(by: {$0.path < $1.path}) {
    let bytes = try file.resourceValues(forKeys: [.fileSizeKey]).fileSize ?? 0
    var trashURL: NSURL?
    try fm.trashItem(at: file, resultingItemURL: &trashURL)
    manifest.append(["source": file.path, "trash": trashURL?.path ?? "", "size_bytes": bytes])
}
let result: [String: Any] = ["kept": keep.path, "moved_to_trash": manifest, "count": manifest.count]
let data = try JSONSerialization.data(withJSONObject: result, options: [.prettyPrinted, .sortedKeys])
try data.write(to: root.appendingPathComponent("verification/xhs_compatible/cleanup.json"))
print("Moved \(manifest.count) old videos to Trash; retained \(keep.lastPathComponent)")
