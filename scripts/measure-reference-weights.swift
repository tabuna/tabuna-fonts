// Compare native named weights with explicit CSS-like weight-axis requests.
// Only font selection, scalar layout and public metadata are inspected.
import Foundation
import AppKit
import CoreText

let output=URL(fileURLWithPath:CommandLine.arguments[1])
let named:[Int:NSFont.Weight]=[100:.ultraLight,200:.thin,300:.light,400:.regular,500:.medium,600:.semibold,700:.bold,800:.heavy,900:.black]
let wght=NSNumber(value:UInt32(0x77676874)),opsz=NSNumber(value:UInt32(0x6f70737a))
var rows=[[String:Any]]()
for size in [16,32,64,128] {
    let regular=CTFontCreateUIFontForLanguage(.system,CGFloat(size),"ru" as CFString)!
    for weight in [100,200,300,400,500,600,700,800,900] {
        let desc=CTFontDescriptorCreateWithAttributes([kCTFontVariationAttribute:[wght:weight,opsz:size]] as CFDictionary)
        let axisFont=CTFontCreateCopyWithAttributes(regular,CGFloat(size),nil,desc)
        let namedFont=NSFont.systemFont(ofSize:CGFloat(size),weight:named[weight]!) as CTFont
        for (mode,font) in [("named",namedFont),("axis",axisFont)] {
            var measurements=[[String:Any]]()
            for ch in "IHEFLНЕІPРDBВвoOоО" {
                let attrs:[NSAttributedString.Key:Any]=[
                    NSAttributedString.Key(kCTFontAttributeName as String):font,
                    NSAttributedString.Key(kCTKernAttributeName as String):0]
                let line=CTLineCreateWithAttributedString(NSAttributedString(string:String(ch),attributes:attrs))
                let box=CTLineGetImageBounds(line,nil)
                measurements.append(["character":String(ch),"advance":CTLineGetTypographicBounds(line,nil,nil,nil),
                                     "bounds":[box.minX,box.minY,box.width,box.height]])
            }
            rows.append(["size":size,"weight":weight,"mode":mode,
                         "unitsPerEm":CTFontGetUnitsPerEm(font),
                         "postScriptName":CTFontCopyPostScriptName(font),
                         "variation":(CTFontCopyVariation(font) as NSDictionary?)?.description ?? "default",
                         "traits":(CTFontCopyTraits(font) as NSDictionary).description,
                         "measurements":measurements])
        }
    }
}
let result:[String:Any]=["os":ProcessInfo.processInfo.operatingSystemVersionString,
                       "scope":"System font selection and scalar layout; no font tables or outlines read","records":rows]
try JSONSerialization.data(withJSONObject:result,options:[.prettyPrinted,.sortedKeys]).write(to:output)
print("Measured \(rows.count) native weight-selection cases.")
