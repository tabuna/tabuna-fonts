// Render the system font and the original Tabuna font through the same CoreText
// pipeline. The system font is only rendered; no outlines or font data are read.
import Foundation
import CoreText
import CoreGraphics
import ImageIO
import UniformTypeIdentifiers
import CryptoKit
import AppKit

let args = CommandLine.arguments
guard args.count >= 3 else {
    fputs("Usage: render-pairs FONT.ttf OUTPUT_DIR [POINT_SIZE] [CHARACTERS] [PIXEL_SCALE] [WEIGHT] [axis|named]\n", stderr)
    exit(1)
}
let fontURL = URL(fileURLWithPath: args[1])
let outputURL = URL(fileURLWithPath: args[2], isDirectory: true)
let pointSize = CGFloat(args.count > 3 ? Double(args[3]) ?? 64 : 64)
let weight = args.count > 6 ? Int(args[6]) ?? 400 : 400
let referenceMode = args.count > 7 ? args[7] : "axis"
guard ["axis","named"].contains(referenceMode) else {fatalError("Reference mode must be axis or named")}
let weightNames:[Int:NSFont.Weight]=[100:.ultraLight,200:.thin,300:.light,400:.regular,500:.medium,600:.semibold,700:.bold,800:.heavy,900:.black]
let characters = args.count > 4 ? args[4] : "аеонДЛЖабвгдёжзийклмпрстуфхцчшщъыьэюяABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
let wordMode=characters.hasPrefix("@") && characters.count > 1
let entries:[String]
if wordMode {
    let input=try JSONSerialization.jsonObject(with:Data(contentsOf:URL(fileURLWithPath:String(characters.dropFirst())))) as! [String:Any]
    entries=input["strings"] as! [String]
} else {entries=characters.map(String.init)}
// Optional magnification keeps the optical size fixed for scalar curve fitting.
// The default proof dimensions and pixel grid are unchanged.
let scale: CGFloat = args.count > 5 ? CGFloat(Double(args[5]) ?? 2) : 2
let magnified=scale > 2
let width = Int(max(magnified ? 64 : 256,wordMode ? pointSize*CGFloat(entries.map {$0.count}.max() ?? 1)*1.1+64 : pointSize*2.7)*scale)
let height = Int(max(magnified ? 64 : 160,pointSize*2.5)*scale)
let originX: CGFloat = 32
let baseline: CGFloat = pointSize*0.6+12
try FileManager.default.createDirectory(at: outputURL, withIntermediateDirectories: true)
let requestedWeight = weightNames[weight]
guard let provider = CGDataProvider(url: fontURL as CFURL), let graphicsFont = CGFont(provider),
      let regularSystemFont = CTFontCreateUIFontForLanguage(.system,pointSize,"ru" as CFString),
      (referenceMode == "axis" || requestedWeight != nil) else {
    fatalError("Unable to load the two fonts")
}
// CSS numeric weights are axis requests, not AppKit named weights. In the
// measured system font, named UltraLight/Black select approximately 30.925/1000.
// Retain named selection only as an explicit historical diagnostic mode.
let systemDescriptor = CTFontDescriptorCreateWithAttributes([kCTFontVariationAttribute:[
    NSNumber(value:UInt32(0x77676874)):NSNumber(value:weight),
    NSNumber(value:UInt32(0x6f70737a)):NSNumber(value:Double(pointSize))]] as CFDictionary)
let systemFont:CTFont = referenceMode == "named"
    ? (weight == 400 ? regularSystemFont : NSFont.systemFont(ofSize:pointSize,weight:requestedWeight!) as CTFont)
    : CTFontCreateCopyWithAttributes(regularSystemFont,pointSize,nil,systemDescriptor)
let plainFont = CTFontCreateWithGraphicsFont(graphicsFont,pointSize,nil,nil)
let wght = NSNumber(value: UInt32(0x77676874))
let opsz = NSNumber(value: UInt32(0x6F70737A))
let axes = CTFontCopyVariationAxes(plainFont) as? [[CFString:Any]] ?? []
var opticalSize = Double(pointSize)
for axis in axes where (axis[kCTFontVariationAxisIdentifierKey] as? NSNumber) == opsz {
    let lo = (axis[kCTFontVariationAxisMinimumValueKey] as! NSNumber).doubleValue
    let hi = (axis[kCTFontVariationAxisMaximumValueKey] as! NSNumber).doubleValue
    opticalSize = min(hi,max(lo,opticalSize))
}
let variations = [wght:NSNumber(value:weight),opsz:NSNumber(value:opticalSize)]
let variedDescriptor = CTFontDescriptorCreateWithAttributes([kCTFontVariationAttribute:variations] as CFDictionary)
let customFont = CTFontCreateCopyWithAttributes(plainFont,pointSize,nil,variedDescriptor)

func render(_ char: String, _ font: CTFont, _ url: URL) -> [String:Any] {
    let space = CGColorSpaceCreateDeviceRGB()
    guard let context = CGContext(data:nil,width:width,height:height,bitsPerComponent:8,
                                  bytesPerRow:width*4,space:space,
                                  bitmapInfo:CGImageAlphaInfo.premultipliedLast.rawValue) else {
        fatalError("No bitmap context")
    }
    context.setFillColor(CGColor(gray:1,alpha:1))
    context.fill(CGRect(x:0,y:0,width:width,height:height))
    context.scaleBy(x:scale,y:scale)
    context.setShouldAntialias(true)
    context.setShouldSmoothFonts(false)
    context.setShouldSubpixelPositionFonts(true)
    context.setShouldSubpixelQuantizeFonts(false)
    context.textMatrix = .identity
    context.textPosition = CGPoint(x:originX,y:baseline)
    var attributes: [NSAttributedString.Key:Any] = [
        NSAttributedString.Key(kCTFontAttributeName as String):font,
        NSAttributedString.Key(kCTForegroundColorAttributeName as String):CGColor(gray:0,alpha:1)
    ]
    if !wordMode {attributes[NSAttributedString.Key(kCTKernAttributeName as String)]=0}
    let string = NSAttributedString(string:char,attributes:attributes)
    let line = CTLineCreateWithAttributedString(string as CFAttributedString)
    CTLineDraw(line,context)
    guard let image=context.makeImage(),
          let destination=CGImageDestinationCreateWithURL(url as CFURL,UTType.png.identifier as CFString,1,nil) else {
        fatalError("No image destination")
    }
    CGImageDestinationAddImage(destination,image,nil)
    guard CGImageDestinationFinalize(destination) else {fatalError("Could not write PNG")}
    let bounds=CTLineGetImageBounds(line,nil)
    let runs=CTLineGetGlyphRuns(line) as! [CTRun]
    let actualFonts=runs.map { run -> String in
        let attrs=CTRunGetAttributes(run) as NSDictionary
        let runFont=attrs[kCTFontAttributeName] as! CTFont
        return CTFontCopyPostScriptName(runFont) as String
    }
    return ["file":url.lastPathComponent,"advance":CTLineGetTypographicBounds(line,nil,nil,nil),
            "inkBounds":[bounds.origin.x,bounds.origin.y,bounds.width,bounds.height],
            "renderedFonts":actualFonts]
}

var records: [[String:Any]]=[]
var seen=Set<Data>()
for char in entries where !seen.contains(Data(char.utf8)) {
    seen.insert(Data(char.utf8))
    let code=char.unicodeScalars.map { String(format:"%04X",$0.value) }.joined(separator:"-")
    let fileID=wordMode ? String(format:"text-%03d",records.count) : code
    let own=render(char,customFont,outputURL.appendingPathComponent("\(fileID)-tabuna.png"))
    let reference=render(char,systemFont,outputURL.appendingPathComponent("\(fileID)-system.png"))
    records.append(["character":char,"codepoint":"U+\(code)","id":fileID,"tabuna":own,"system":reference])
}
_ = render("о",systemFont,outputURL.appendingPathComponent("self-test-a.png"))
_ = render("о",systemFont,outputURL.appendingPathComponent("self-test-b.png"))
let fontHash = SHA256.hash(data:try Data(contentsOf:fontURL)).map { String(format:"%02x",$0) }.joined()
let settings: [String:Any] = [
    "renderer":"CoreText / CoreGraphics, same offscreen context settings",
    "os":ProcessInfo.processInfo.operatingSystemVersionString,
    "pointSize":pointSize,"pixelScale":scale,"canvas":[width,height],
    "originPixels":[originX*scale,CGFloat(height)-baseline*scale],
    "weight":weight,"customOpticalSize":opticalSize,
    "referenceWeightMode":referenceMode,
    "textMode":wordMode,"kerning":wordMode ? "standard" : "disabled for isolated glyphs",
    "antialias":"grayscale; subpixel positioning on; subpixel quantization off",
    "systemPostScriptName":CTFontCopyPostScriptName(systemFont),
    "systemVariation":(CTFontCopyVariation(systemFont) as NSDictionary?)?.description ?? "system default",
    "customPostScriptName":CTFontCopyPostScriptName(customFont),
    "customVariation":(CTFontCopyVariation(customFont) as NSDictionary?)?.description ?? "none",
    "systemTraits":(CTFontCopyTraits(systemFont) as NSDictionary).description,
    "fontSHA256":fontHash,
    "selfTest":["self-test-a.png","self-test-b.png"],
    "alignment":"shared pen origin and baseline; no image registration, scaling or contour extraction",
    "records":records
]
let data=try JSONSerialization.data(withJSONObject:settings,options:[.prettyPrinted,.sortedKeys,.fragmentsAllowed])
try data.write(to:outputURL.appendingPathComponent("render-settings.json"))
print("Rendered \(records.count) pairs at \(pointSize) pt, \(Int(scale))× into \(outputURL.path)")
