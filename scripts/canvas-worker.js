/* Independent Canvas measurements: no DOM font rendering in this worker. */
self.onmessage=async({data:{fontURL,characters,sizes,weights=[400],nativeWeightReportURL,hashPixels=false}})=>{
  try{
    const response=await fetch(fontURL,{cache:'no-store'});
    if(!response.ok)throw new Error(`Font HTTP ${response.status}`);
    const bytes=await response.arrayBuffer();
    const fontHash=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)),b=>b.toString(16).padStart(2,'0')).join('');
    const face=new FontFace('TabunaWorkerProbe',bytes,{weight:'100 900'});
    await face.load();self.fonts.add(face);
    function raster(text,size,family,weight){
      const canvas=new OffscreenCanvas(320,220),ctx=canvas.getContext('2d',{willReadFrequently:true});
      ctx.fillStyle='#fff';ctx.fillRect(0,0,320,220);
      ctx.fillStyle='#000';ctx.font=`${weight} ${size}px ${family}`;ctx.fontKerning='normal';ctx.textBaseline='alphabetic';
      ctx.fillText(text,32,160);
      return {advance:ctx.measureText(text).width,pixels:ctx.getImageData(0,0,320,220).data};
    }
    const records=[];
    for(const weight of weights)for(const size of sizes)for(const text of characters){
      const own=raster(text,size,'TabunaWorkerProbe',weight),system=raster(text,size,'system-ui',weight),repeat=raster(text,size,'system-ui',weight);
      let differentPixels=0,selfTestPixels=0,absoluteInkError=0;
      for(let i=0;i<own.pixels.length;i+=4){
        const difference=Math.abs(own.pixels[i]-system.pixels[i]);
        if(difference)differentPixels++;absoluteInkError+=difference;
        if(system.pixels[i]!==repeat.pixels[i])selfTestPixels++;
      }
      const hashes={};
      if(hashPixels){
        for(const [key,pixels] of [['ownRasterSHA256',own.pixels],['systemRasterSHA256',system.pixels]]){
          hashes[key]=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',pixels)),b=>b.toString(16).padStart(2,'0')).join('');
        }
      }
      records.push({...hashes,text,size,weight,differentPixels,selfTestPixels,absoluteInkError,ownAdvance:own.advance,systemAdvance:system.advance,
        exactPixels:differentPixels===0&&selfTestPixels===0,
        exactAdvance:own.advance===system.advance,
        completeMatch:differentPixels===0&&selfTestPixels===0&&own.advance===system.advance});
    }
    let nativeComparison;
    if(nativeWeightReportURL){
      const response=await fetch(nativeWeightReportURL,{cache:'no-store'});
      if(!response.ok)throw new Error(`Native report HTTP ${response.status}`);
      const native=await response.json();
      nativeComparison={referenceURL:nativeWeightReportURL,rows:[]};
      for(const mode of ['named','axis'])for(const r of records){
        const group=native.records.find(n=>n.mode===mode&&n.size===r.size&&n.weight===r.weight);
        const n=group.measurements.find(n=>n.character===r.text);
        const rounded=Math.round(n.advance*group.unitsPerEm/r.size)*r.size/group.unitsPerEm;
        nativeComparison.rows.push({mode,weight:r.weight,size:r.size,text:r.text,nativeAdvance:n.advance,
          roundedNativeAdvance:rounded,browserAdvance:r.systemAdvance,exact:rounded===r.systemAdvance});
      }
    }
    self.postMessage({userAgent:navigator.userAgent,fontHash,weights,scale:1,canvas:[320,220],origin:[32,160],nativeComparison,
      renderer:'OffscreenCanvas in dedicated Worker; no DOM font rendering; no image registration',records,
      exactPixelCount:records.filter(r=>r.exactPixels).length,exactAdvanceCount:records.filter(r=>r.exactAdvance).length,
      completeCount:records.filter(r=>r.completeMatch).length});
  }catch(error){self.postMessage({error:error.message})}
};
