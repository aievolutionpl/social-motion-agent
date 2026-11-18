const assert = require("node:assert/strict");
const { chromium } = require("playwright");

async function gallery(page, [url, portable, destination]) {
  await page.goto(url);
  const studio = page.locator("article").filter({has: page.getByRole("heading", {name: "Studio", exact: true})});
  await studio.waitFor();
  assert.equal(await page.locator("video[controls]").count(), 3);
  await studio.locator(".star").nth(3).click();
  await studio.getByText("Zapisano dla agenta.").waitFor();
  await studio.locator("textarea").fill("Większy kadr");
  await studio.getByRole("button").click();
  await studio.getByText("Zapisano dla agenta.").waitFor();
  await page.getByLabel("Uwagi do całego filmu").fill("Dłuższe pauzy");
  await page.getByRole("button", {name: "Zapisz uwagi do filmu"}).click();
  await page.locator(".general").getByText("Zapisano dla agenta.").waitFor();
  await page.reload();
  await studio.waitFor();
  assert.equal(await studio.locator("input:checked").inputValue(), "4");
  assert.equal(await studio.locator("textarea").inputValue(), "Większy kadr");
  assert.equal(await page.getByLabel("Uwagi do całego filmu").inputValue(), "Dłuższe pauzy");
  await page.goto(portable);
  await page.getByText(/Po ocenie pobierz/).waitFor();
  await page.getByLabel("Uwagi do całego filmu").fill("Jaśniejsze tło");
  await page.getByRole("button", {name: "Zapisz uwagi do filmu"}).click();
  await page.locator(".general").getByText(/Pobierz ją dla agenta/).waitFor();
  const exported = page.waitForEvent("download");
  await page.getByRole("button", {name: "Pobierz opinie dla agenta"}).click();
  await (await exported).saveAs(destination);
}

async function scene(page, [url]) {
  await page.goto(url);
  await page.waitForFunction(() => typeof window.seek === "function");
  const stage = page.locator("#root");
  async function frame(at) {
    await page.evaluate(t => window.seek(t), at);
    return stage.screenshot();
  }
  const before = await frame(.15);
  const after = await frame(3.5);
  assert.ok(!before.equals(after), "The scene must move");
  assert.ok(before.equals(await frame(.15)), "Seeking back must restore the original pixels");
}

(async () => {
  const browser = await chromium.launch({headless: true,
    ...(process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH ? {executablePath: process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH} : {})});
  try {
    const page = await browser.newPage({viewport: {width: 1100, height: 720}});
    page.setDefaultTimeout(8000);
    const errors = [];
    page.on("pageerror", error => errors.push(error.message));
    const [mode, ...args] = process.argv.slice(2);
    if (mode === "gallery") await gallery(page, args);
    else if (mode === "scene") await scene(page, args);
    else throw new Error("Expected gallery or scene");
    assert.deepEqual(errors, []);
  } finally {
    await browser.close();
  }
})().catch(error => { console.error(error); process.exitCode = 1; });
