const { chromium } = require('playwright');
const assert = require('node:assert/strict');
const crypto = require('node:crypto');
(async()=>{
 const browser=await chromium.launch({headless:true});
 try {
  const page=await browser.newPage();
  for (const slug of ['riso-print','decollage-time-layers','optical-moire']) {
   await page.goto(process.argv[2]+'?style='+slug);
   await page.waitForFunction(()=>window.motionReady===true);
   assert.equal(await page.locator('#style').inputValue(),slug);
   const hash=async t=>{const png=await page.evaluate(t=>{window.seek(t);return document.querySelector('canvas').toDataURL('image/png')},t);return crypto.createHash('sha256').update(png).digest('hex')};
   const zero=await hash(0), later=await hash(2), again=await hash(0);
   assert.equal(zero,again,slug+' seek must be history-independent');
   assert.notEqual(zero,later,slug+' must change rendered pixels');
   await page.selectOption('#style','optical-moire');
   await page.selectOption('#style',slug);
   assert.equal(await hash(0),zero,slug+' must recover after switching');
   console.log(slug+' deterministic and changes pixels');
  }
 } finally {await browser.close()}
})().catch(e=>{console.error(e);process.exit(1)});
