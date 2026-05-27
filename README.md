# Admin Finder

<p align="center">
  <img src="https://img.shields.io/badge/Author-devUmut35-red?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Tool-Admin%20Finder-black?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Python-3.x-blue?style=for-the-badge&logo=python&logoColor=white" />
</p>

<p align="center">
  <b>Yetkili testler, CTF ve lab ortamları için hızlı admin panel path kontrol aracı.</b>
</p>

---

## Hakkında

**Admin Finder**, hedef web sitesi üzerinde yaygın admin/login pathlerini kontrol eden basit ve hızlı bir Python aracıdır.

Araç, verilen hedef URL üzerinde wordlist içindeki yolları dener ve sonuçları temiz bir şekilde terminale yazar. Tarama sonunda bulunan veya önemli görünen sonuçları ayrıca **FOUND RESULTS** bölümünde tekrar listeler.

**Signature:** `devUmut35`

---

## Özellikler

- Hızlı tarama
- Thread desteği
- 300+ path içeren wordlist
- Sonuçları dosyaya kaydetme
- Custom wordlist desteği

---

## Kurulum

Repoyu indir:

```bash
git clone https://github.com/devUmut35/admin-finder.git
cd admin-finder
```

Gerekli paketi kur:

```bash
pip install -r requirements.txt
```

---

## Kullanım

Direkt tarama:

```bash
py admin_finder.py https://example.com
```

Alternatif kullanım:

```bash
py admin_finder.py -u https://example.com
```

---

## Interactive Kullanım

Programı başlat:

```bash
py admin_finder.py
```

Sonra komut gir:

```txt
scan https://example.com
```

---

## Örnek Komutlar

Daha hızlı tarama:

```bash
py admin_finder.py https://example.com -t 80 --timeout 1.5
```

404 sonuçlarını gizleme:

```bash
py admin_finder.py https://example.com --hide-404
```

Bulunan sonuçları dosyaya kaydetme:

```bash
py admin_finder.py https://example.com -o results.txt
```

Custom wordlist kullanma:

```bash
py admin_finder.py https://example.com -w wordlists/admin_paths.txt
```

---

## Interactive Komutlar

```txt
scan https://example.com
scan https://example.com -t 80 --timeout 1.5
scan https://example.com --hide-404
scan https://example.com -o results.txt
clear
help
exit
```

---

## Örnek Çıktı

```txt
[001/311] https://example.com/admin/ -> NOT FOUND (404)
[002/311] https://example.com/admin/login -> NOT FOUND (404)
[003/311] https://example.com/admin/index.php -> REDIRECT (301) | https://example.com/admin/
[004/311] https://example.com/wp-admin/ -> FORBIDDEN (403)
[005/311] https://example.com/xmlrpc.php -> FOUND (200)
```

Tarama sonunda bulunan sonuçlar tekrar gösterilir:

```txt
FOUND RESULTS
[003/311] https://example.com/admin/index.php -> REDIRECT (301) | https://example.com/admin/
[004/311] https://example.com/wp-admin/ -> FORBIDDEN (403)
[005/311] https://example.com/xmlrpc.php -> FOUND (200)
```

---

## Parametreler

| Parametre | Açıklama |
|---|---|
| `-u`, `--url` | Hedef URL |
| `-w`, `--wordlist` | Custom wordlist dosyası |
| `-o`, `--output` | Bulunan sonuçları dosyaya kaydeder |
| `-t`, `--threads` | Thread sayısı |
| `--timeout` | İstek zaman aşımı süresi |
| `--hide-404` | 404 sonuçlarını gizler |

---

## Sonuç Etiketleri

| Etiket | Anlamı |
|---|---|
| `FOUND` | Sayfa mevcut |
| `REDIRECT` | Yönlendirme var |
| `FORBIDDEN` | Erişim engelli, path var olabilir |
| `AUTH` | Giriş gerekebilir |
| `MAYBE` | Endpoint var olabilir |
| `NOT FOUND` | Path bulunamadı |
| `ERROR` | İstek başarısız oldu |

---

## Proje Yapısı

```txt
admin-finder/
├── admin_finder.py
├── requirements.txt
├── README.md
├── .gitignore
└── wordlists/
    └── admin_paths.txt
```

---

## Gereksinimler

```txt
requests>=2.31.0
```

---

## Yasal Uyarı

Bu araç yalnızca aşağıdaki ortamlar için hazırlanmıştır:

- Kendi sistemlerin
- CTF hedefleri
- Lab ortamları
- Yetkili güvenlik testleri

İzinsiz sistemlerde kullanmak doğru değildir.

---

## Geliştirici

Geliştiren: **devUmut35**
