// Measure actual text layout. Reference font files and outlines are not read.
import Foundation
import CoreText
import CoreGraphics
import AppKit
import CryptoKit

let args=CommandLine.arguments
guard args.count==6 || args.count==7 else {
    fputs("Usage: measure-text FONT.ttf INPUT.json OUTPUT.json SIZE WEIGHT [axis|named]\n",stderr);exit(1)
}
let fontURL=URL(fileURLWithPath:args[1]),inputURL=URL(fileURLWithPath:args[2]),outputURL=URL(fileURLWithPath:args[3])
let size=CGFloat(Double(args[4])!),weight=Double(args[5])!
let weights:[Int:NSFont.Weight]=[100:.ultraLight,200:.thin,300:.light,400:.regular,500:.medium,600:.semibold,700:.bold,800:.heavy,900:.black]
guard weight.isFinite && weight >= 100 && weight <= 900,let provider=CGDataProvider(url:fontURL as CFURL),let graphicsFont=CGFont(provider) else {fatalError("Cannot load font or weight")}
let referenceMode=args.count==7 ? args[6] : "axis"
guard ["axis","named"].contains(referenceMode) else {fatalError("Reference mode must be axis or named")}
let requestedWeight=weights[Int(weight)] ?? .regular
if referenceMode == "named" && (weight != Double(Int(weight)) || weights[Int(weight)] == nil) {fatalError("Named reference requires a standard weight")}
let regular=CTFontCreateUIFontForLanguage(.system,size,"ru" as CFString)!
let systemDescriptor=CTFontDescriptorCreateWithAttributes([kCTFontVariationAttribute:[
    NSNumber(value:UInt32(0x77676874)):NSNumber(value:weight),
    NSNumber(value:UInt32(0x6f70737a)):NSNumber(value:Double(size))]] as CFDictionary)
let system=referenceMode == "named" ? NSFont.systemFont(ofSize:size,weight:requestedWeight) as CTFont : CTFontCreateCopyWithAttributes(regular,size,nil,systemDescriptor)
let raw=CTFontCreateWithGraphicsFont(graphicsFont,size,nil,nil)
let variation=[NSNumber(value:UInt32(0x77676874)):NSNumber(value:weight),NSNumber(value:UInt32(0x6f70737a)):NSNumber(value:Double(size))]
let descriptor=CTFontDescriptorCreateWithAttributes([kCTFontVariationAttribute:variation] as CFDictionary)
let own=CTFontCreateCopyWithAttributes(raw,size,nil,descriptor)
let input=try JSONSerialization.jsonObject(with:Data(contentsOf:inputURL)) as! [String:Any]
let pairMode=input["characters"] != nil
let characters=(input["characters"] as? String ?? "").map(String.init)
let strings=pairMode ? characters.flatMap { a in characters.map {a+$0} } : input["strings"] as! [String]

func measure(_ text:String,_ font:CTFont,_ kerning:Bool)->(Double,[String],[[String:Any]]) {
    var attributes:[NSAttributedString.Key:Any]=[NSAttributedString.Key(kCTFontAttributeName as String):font]
    if !kerning {attributes[NSAttributedString.Key(kCTKernAttributeName as String)]=0}
    // A ligature would confound pair-position measurement. Validation strings
    // retain the platform's default ligature behavior.
    if pairMode {attributes[NSAttributedString.Key(kCTLigatureAttributeName as String)]=0}
    let line=CTLineCreateWithAttributedString(NSAttributedString(string:text,attributes:attributes))
    let runs=CTLineGetGlyphRuns(line) as! [CTRun]
    let fonts=Array(Set(runs.map {run -> String in
        let attrs=CTRunGetAttributes(run) as NSDictionary
        return CTFontCopyPostScriptName(attrs[kCTFontAttributeName] as! CTFont) as String
    })).sorted()
    var layout:[[String:Any]]=[]
    if !pairMode {
        for run in runs {
            let count=CTRunGetGlyphCount(run)
            var indices=[CFIndex](repeating:0,count:count),advances=[CGSize](repeating:.zero,count:count),glyphs=[CGGlyph](repeating:0,count:count)
            CTRunGetStringIndices(run,CFRange(location:0,length:0),&indices)
            CTRunGetAdvances(run,CFRange(location:0,length:0),&advances)
            CTRunGetGlyphs(run,CFRange(location:0,length:0),&glyphs)
            let attrs=CTRunGetAttributes(run) as NSDictionary
            let runFont=attrs[kCTFontAttributeName] as! CTFont
            var bounds=[CGRect](repeating:.zero,count:count)
            CTFontGetBoundingRectsForGlyphs(runFont,.default,&glyphs,&bounds,count)
            for i in 0..<count {layout.append(["index":indices[i],"advance":advances[i].width,"glyph":glyphs[i],
                "bounds":[bounds[i].minX,bounds[i].minY,bounds[i].width,bounds[i].height]])}
        }
    }
    return (CTLineGetTypographicBounds(line,nil,nil,nil),fonts,layout)
}
var rows:[[String:Any]]=[]
var zeroPairs=0,fallbacks=0
let ownName=CTFontCopyPostScriptName(own) as String,systemName=CTFontCopyPostScriptName(system) as String
for text in strings {
    autoreleasepool {
        let a=measure(text,own,true),b=measure(text,system,true)
        let az=measure(text,own,false),bz=measure(text,system,false)
        let adjustment=(b.0-bz.0)*2048/Double(size)
        let ours=(a.0-az.0)*2048/Double(size)
        let fallback=a.1 != [ownName] || b.1 != [systemName]
        if fallback {fallbacks+=1}
        if pairMode && adjustment==0 && ours==0 && !fallback {zeroPairs+=1;return}
        var row:[String:Any]=["text":text,"own":a.0,"system":b.0,"ownUnkerned":az.0,"systemUnkerned":bz.0,
                     "systemAdjustment":adjustment,"ownAdjustment":ours,"fallback":fallback]
        if !pairMode {
            row["ownLayout"]=a.2;row["systemLayout"]=b.2
            row["ownUnkernedLayout"]=az.2;row["systemUnkernedLayout"]=bz.2
        }
        rows.append(row)
    }
}
let hash=SHA256.hash(data:try Data(contentsOf:fontURL)).map {String(format:"%02x",$0)}.joined()
let result:[String:Any]=["fontSHA256":hash,"inputSHA256":SHA256.hash(data:try Data(contentsOf:inputURL)).map {String(format:"%02x",$0)}.joined(),
    "os":ProcessInfo.processInfo.operatingSystemVersionString,"referenceFont":systemName,"ownFont":ownName,
    "pointSize":size,"weight":weight,"pairMode":pairMode,"ligatures":pairMode ? "disabled" : "platform default",
    "referenceWeightMode":referenceMode,
    "kerning":"attribute omitted for normal layout; explicit zero for disabled layout",
    "measuredCount":strings.count,"omittedZeroPairs":zeroPairs,"fallbackCount":fallbacks,"records":rows]
try FileManager.default.createDirectory(at:outputURL.deletingLastPathComponent(),withIntermediateDirectories:true)
try JSONSerialization.data(withJSONObject:result,options:[.prettyPrinted,.sortedKeys]).write(to:outputURL)
print("Measured \(strings.count) strings, \(rows.count) recorded, \(zeroPairs) zero pairs, \(fallbacks) fallback strings at \(size) / \(weight)")
