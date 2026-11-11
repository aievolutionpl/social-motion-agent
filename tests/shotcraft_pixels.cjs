// Browser smoke test: seek is deterministic, preview frames change with time.
const {chromium} = require('playwright');
const assert = require('node:assert/strict');
(async () => {
  const browser = await chromium.launch({headless: true});
  try {
    const page = await browser.newPage({viewport:{width:1280,height:900}});
    page.on('pageerror', e => { throw e; });
    await page.goto(process.argv[2], {waitUntil:'networkidle', timeout:30000});
    await page.waitForFunction(() => window.shotcraftReady === true, {timeout:10000});
    const shots=['carousel-3d','card-flock-tumble','flying-words',
                 'value-stagger-gradient','before-after-slider-scrub'];
    for (const shot of shots) {
      await page.evaluate(s => window.selectShot(s), shot);
      await page.evaluate(() => window.seek(0.3));
      const a=await page.locator('canvas').evaluate(c=>c.toDataURL());
      await page.evaluate(() => window.seek(3.8));
      const b=await page.locator('canvas').evaluate(c=>c.toDataURL());
      assert.notEqual(a,b, shot+' does not animate');
      await page.evaluate(() => window.seek(0.3));
      const c=await page.locator('canvas').evaluate(c=>c.toDataURL());
      assert.equal(a,c,shot+' not deterministic after reverse seek');
      assert.ok(a.length>5000,shot+' blank');
    }
    console.log('ShotCraft browser pixels passed: '+shots.length+' previews.');
  } finally { await browser.close(); }
})().catch(e=>{console.error(e);process.exitCode=1;});
