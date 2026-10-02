
(() => {
  const key = "cellarbrations_extraction";

  const saved = JSON.parse(
    localStorage.getItem(key) || '{"urls":[],"results":[],"index":0}'
  );

  const el = document.querySelector(
    '[data-testid="pdpDangerouslySetDecription-span-testId"]'
  );

  if (!el) {
    console.log("No product description found on this page.");
    return;
  }

  const parts = el.innerHTML
    .split(/<br\s*\/?>/i)
    .map(html => {
      const temp = document.createElement("div");
      temp.innerHTML = html;
      return temp.innerText.trim();
    })
    .filter(Boolean);

  const attributeIndex = parts.findIndex(text =>
    /^(Alcohol Volume|Pack Format|Standard Drinks|Pack Type|Country of Origin):/i.test(text)
  );

  const attributes = Object.fromEntries(
    parts.slice(attributeIndex < 0 ? parts.length : attributeIndex)
      .map(text => {
        const i = text.indexOf(":");
        return i < 0 ? null : [text.slice(0, i).trim(), text.slice(i + 1).trim()];
      })
      .filter(Boolean)
  );

  const result = {
    product_id: location.pathname.match(/id-(\d+)/)?.[1] ?? null,
    product_url: location.href,
    description: parts.slice(
      0, attributeIndex < 0 ? parts.length : attributeIndex
    ).join(" "),
    attributes
  };

  console.log("Extracted product:", result);
})();