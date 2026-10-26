// Browser fallback for ksp_stock.py. Same JSON shape.
// Open any ksp.co.il page in a real browser (so the request carries KSP's cookies),
// then pass this whole file as the `function` of a browser evaluate call after
// replacing the two placeholders:
//   __TARGET__   search query, item URL, or item id (uin)
//   __BRANCHES__ JSON array of branch ids/keys/name substrings, e.g. ["57"]; [] = all
async () => {
  const target = "__TARGET__";
  const wanted = __BRANCHES__;
  const limit = 8;
  const api = async (p) => {
    const r = await fetch("/m_action/api" + p);
    if (!r.ok) throw new Error(`HTTP ${r.status} on ${p}`);
    return r.json();
  };
  const match = (s, key) => wanted.some((w) => {
    const wl = String(w).toLowerCase();
    return w === s.id || wl === key.toLowerCase() || s.name.toLowerCase().includes(wl) || key.toLowerCase().includes(wl);
  });
  // mlay takes the catalogue number (uinsql), not the URL id.
  const stock = async (sku) => {
    const stores = ((await api(`/mlay/${sku}`)).result || {}).stores || {};
    const rows = Object.entries(stores).map(([key, s]) => ({
      id: s.id, key, name: s.name, region: s.region, in_stock: s.qnt > 0, last_unit: !!s.isLastItem,
    }));
    return [rows.filter((r) => r.in_stock).length, wanted.length ? rows.filter((r) => match(r, r.key)) : rows];
  };
  const record = async (uin, sku, name, price, eilat) => {
    const [n, branches] = await stock(sku);
    return { id: +uin, sku: String(sku), name, price_ils: price, eilat_price_ils: eilat || null,
      url: `https://ksp.co.il/web/item/${uin}`, branches_in_stock: n, branches };
  };
  const out = { retailer: "ksp", checked_at: new Date().toISOString(), branch_filter: wanted.length ? wanted : "all", items: [] };
  const m = target.match(/\/item\/(\d+)/) || target.match(/^(\d+)$/);
  if (m) {
    const d = (await api(`/item/${m[1]}`)).result.data;
    out.items.push(await record(m[1], d.uinsql, d.name, d.price, d.eilatPrice));
  } else {
    const res = (await api("/category/?search=" + encodeURIComponent(target))).result;
    out.products_total = res.products_total;
    for (const it of (res.items || []).slice(0, limit)) {
      out.items.push(await record(it.uin, it.uinsql, it.name, it.price, it.eilatPrice));
    }
  }
  return out;
}
