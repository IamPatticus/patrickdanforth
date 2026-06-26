# DNS Setup for patrickdanforth.com → GitHub Pages

**Registrar:** Squarespace
**Target:** GitHub Pages (iampatticus.github.io/patrickdanforth/)

## DNS Records to Add

| Type | Host/Name | Points to |
|------|-----------|-----------|
| CNAME | www | iampatticus.github.io |
| A | @ | 185.199.108.153 |
| A | @ | 185.199.109.153 |
| A | @ | 185.199.110.153 |
| A | @ | 185.199.111.153 |

## Steps
1. Remove forwarding rule ✅ (done)
2. Add DNS records above (in progress)
3. GitHub Pages settings → Custom domain → patrickdanforth.com → Save
4. Wait for DNS propagation + SSL provisioning (~5-30 min)

## CNAME file
Already committed to repo at root: `patrickdanforth.com`
