const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const crypto=require('node:crypto');
(async()=>{
 const browser=await chromium.launch({headless:true, ...(process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH ? {executablePath:process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH} : {})});
 try{
  const page=await browser.newPage({viewport:{width:1080,height:1920},deviceScaleFactor:1});
  const errors=[];page.on('pageerror',error=>errors.push(error.message));
  await page.goto(process.argv[2]);await page.evaluate(()=>window.__ready);
  const capture=await page.context().newCDPSession(page);
  // Capture the paused scene directly; avoid Playwright's animated-layout stabilization.
  const hash=async t=>{
   await page.evaluate(t=>{window.seek(t);return new Promise(resolve=>requestAnimationFrame(()=>resolve()))},t);
   const png=await capture.send('Page.captureScreenshot',{format:'png',fromSurface:true,captureBeyondViewport:false});
   return crypto.createHash('sha256').update(Buffer.from(png.data,'base64')).digest('hex');
  };
  const before=await hash(.6),after=await hash(1.3),again=await hash(.6);
  assert.equal(before,again,'Seeking back must reproduce the same pixels');
  assert.notEqual(before,after,'Timed captions and camera must change rendered pixels');
  const state=await page.evaluate(()=>({text:document.querySelector('#caption-0').textContent,
   caption:getComputedStyle(document.querySelector('#caption-0')).visibility,
   next:getComputedStyle(document.querySelector('#caption-1')).visibility,
   behind:Number(getComputedStyle(document.querySelector('#accent-0')).zIndex),
   person:Number(getComputedStyle(document.querySelector('.foreground')).zIndex)}));
  assert.equal(state.text,'Zażółć gęślą jaźń');assert.equal(state.caption,'visible');assert.equal(state.next,'hidden');
  assert.ok(state.behind<state.person,'Subject must paint over the behind-subject text');
  await page.evaluate(()=>{window.__timelines.main.seek(1.3,true)});
  assert.equal(await page.locator('#caption-1').evaluate(el=>getComputedStyle(el).visibility),'visible','Renderer seeks that suppress callbacks must still show captions');
  await page.evaluate(()=>window.seek(3));assert.equal(await page.locator('#caption-1').evaluate(el=>getComputedStyle(el).visibility),'hidden');
  assert.deepEqual(errors,[]);console.log('Walk-talk: deterministic pixels, Polish text, caption timing and layer order verified');
 }finally{await browser.close()}
})().catch(error=>{console.error(error);process.exit(1)});
