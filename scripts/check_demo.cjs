// Regression checks for text enlargement and numerical UI. Requires Playwright.
const {chromium} = require('playwright');
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
(async () => {
  const out = process.env.DEMO_CHECK_OUT || 'build/demo-check';
  fs.mkdirSync(out, {recursive:true});
  const browser = await chromium.launch({headless:true, ...(process.env.CHROME_PATH ? {executablePath:process.env.CHROME_PATH} : {})});
  const results = [];
  try {
    for (const width of [320,375,768,1280]) for (const root of [16,32]) for (const theme of ['light','dark']) {
      const page = await browser.newPage({viewport:{width,height:900},colorScheme:theme});
      await page.goto(process.env.DEMO_URL || 'http://127.0.0.1:4173/');
      await page.evaluate(() => document.fonts.ready);
      await page.addStyleTag({content:`html{font-size:${root}px}`});
      await page.selectOption('#sample-role','body');
      await page.check('#compare');
      await page.click('#ui-save');
      await page.locator('.extended-reading summary').click();
      const result = await page.evaluate(() => {
        const style = s => getComputedStyle(document.querySelector(s));
        const controls = [...document.querySelectorAll('button,select,input,textarea')].filter(e=>e.getClientRects().length);
        const clippedControls = controls.filter(e=> {const r=e.getBoundingClientRect(); return r.left<0 || r.right>innerWidth+1;}).map(e=>e.id || e.outerHTML.slice(0,120));
        const clippedText = [...document.querySelectorAll('h1,h2,h3,.controls>label,.facts>div,.glyph small')].filter(e=>e.scrollWidth>e.clientWidth+1).map(e=>e.textContent.trim());
        const table = document.querySelector('.table-sample');
        const value = table.querySelector('td:last-child'), original=value.textContent;
        const timers=['00:00:00','11:11:11','88:88:88','12:34:56','09:59:59','10:00:00'];
        const timerWidths=timers.map(text=>{value.textContent=text;const r=document.createRange();r.selectNodeContents(value);return r.getBoundingClientRect().width;});
        value.textContent=original;
        return {timerWidths, viewport:innerWidth, scrollWidth:document.documentElement.scrollWidth, clippedControls, clippedText,
          articleSize:style('.article-sample>p:not(.overline)').fontSize, uiSize:style('#ui-save').fontSize,
          exactSpecimenSize:style('#sample-text').fontSize,
          feedback:document.querySelector('#ui-feedback').textContent,
          fontLoaded:document.fonts.check('400 18px "Tabuna Sans"','Ясность'),
          glyphCount:document.querySelectorAll('.glyph').length,
          table:{width:table.clientWidth,scroll:table.scrollWidth,focusable:table.tabIndex===0,label:table.getAttribute('aria-label')}};
      });
      result.pass = Math.max(...result.timerWidths)-Math.min(...result.timerWidths)<0.02 && result.scrollWidth<=width+1 && !result.clippedControls.length && !result.clippedText.length && result.articleSize===`${root}px` && result.uiSize===`${root}px` && result.exactSpecimenSize==='18px' && result.glyphCount===189 && result.fontLoaded && result.feedback==='Настройки образца сохранены.';
      results.push({width,root,theme,...result});
      if (width===320 && root===32 && theme==='light') {
        await page.locator('.hero').screenshot({path:path.join(out,'enlarged-hero.png')});
        await page.locator('.controls').screenshot({path:path.join(out,'enlarged-controls.png')});
        await page.locator('.reading-grid').screenshot({path:path.join(out,'enlarged-reading.png')});
      }
      if (width===1280 && root===16 && theme==='light') {await page.evaluate(()=>scrollTo(0,0));await page.screenshot({path:path.join(out,'desktop.png')});}
      await page.close();
    }
  } finally {await browser.close();}
  const hashes=Object.fromEntries(['index.html','demo.css','demo.js','dist/TabunaSansVariable.woff2'].map(f=>[f,crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex')]));
  const report={method:'Chrome headless, CSS root text enlargement; not native Dynamic Type or real browser zoom',hashes,results,passed:results.every(r=>r.pass)};
  fs.writeFileSync(path.join(out,'report.json'),JSON.stringify(report,null,2)+'\n');
  console.log(JSON.stringify({passed:report.passed,conditions:results.length,failures:results.filter(r=>!r.pass)},null,2));
  if(!report.passed)process.exitCode=1;
})().catch(e=>{console.error(e);process.exitCode=1;});
