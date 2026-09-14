"""Build a batch entry point around the unchanged native renderer."""
import hashlib
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def renderer():
    source = (ROOT/'scripts/render-pairs.swift').read_text()
    marker = 'let args = CommandLine.arguments'
    assert source.count(marker) == 1
    imports, body = source.split(marker)
    batch = imports+'func renderBatchJob(_ args: [String]) throws {\n'+body+'\n}\n'+'''
let batchData = try Data(contentsOf: URL(fileURLWithPath: CommandLine.arguments[1]))
let batchJobs = try JSONSerialization.jsonObject(with: batchData) as! [[String]]
for job in batchJobs { try autoreleasepool { try renderBatchJob(job) } }
'''
    digest = hashlib.sha256(batch.encode()).hexdigest()
    folder = ROOT/'build/native-refinement'
    binary, stamp = folder/'render-batch', folder/'source.sha256'
    if not binary.exists() or not stamp.exists() or stamp.read_text().strip() != digest:
        folder.mkdir(parents=True, exist_ok=True)
        generated = folder/'render-batch.swift'
        generated.write_text(batch)
        cache = Path('/tmp/tabuna-swift-module-cache')
        cache.mkdir(parents=True, exist_ok=True)
        subprocess.run(['swiftc', '-module-cache-path', str(cache), str(generated), '-o', str(binary)], check=True)
        stamp.write_text(digest+'\n')
    return binary
