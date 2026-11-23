import requests
import xmltodict

PUBMED_SEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
PUBMED_FETCH_URL  = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
PMC_FETCH_URL     = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
PMID_TO_PMCID_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi"


def search_pubmed(query: str, max_results: int = 5) -> list[str]:
    params = {
        "db": "pubmed",
        "term": query,
        "retmax": max_results,
        "retmode": "xml",
    }
    response = requests.get(PUBMED_SEARCH_URL, params=params)
    data = xmltodict.parse(response.text)
    ids = data["eSearchResult"]["IdList"].get("Id") if data["eSearchResult"]["IdList"] else None
    if not ids:
        return []
    return ids if isinstance(ids, list) else [ids]


def fetch_abstract(pubmed_id: str) -> dict | None:
    params = {
        "db": "pubmed",
        "id": pubmed_id,
        "retmode": "xml",
        "rettype": "abstract",
    }
    response = requests.get(PUBMED_FETCH_URL, params=params)
    data = xmltodict.parse(response.text)

    try:
        article = data["PubmedArticleSet"]["PubmedArticle"]["MedlineCitation"]["Article"]
        title   = article.get("ArticleTitle", "")
        abstract = article.get("Abstract", {}).get("AbstractText", "")

        if isinstance(abstract, list):
            abstract = " ".join(
                a.get("#text", a) if isinstance(a, dict) else a
                for a in abstract
            )
        elif isinstance(abstract, dict):
            abstract = abstract.get("#text", "")

        return {"title": title, "text": abstract, "source": f"pubmed_{pubmed_id}", "page": 1}
    except (KeyError, TypeError):
        return None


def convert_pmid_to_pmcid(pubmed_id: str) -> str | None:
    params = {
        "dbfrom": "pubmed",
        "db": "pmc",
        "id": pubmed_id,
        "retmode": "xml",
    }
    response = requests.get(PMID_TO_PMCID_URL, params=params)
    data = xmltodict.parse(response.text)
    try:
        links = data["eLinkResult"]["LinkSet"]["LinkSetDb"]["Link"]
        if isinstance(links, list):
            return links[0]["Id"]
        return links["Id"]
    except (KeyError, TypeError):
        return None


def fetch_pmc_fulltext(pubmed_id: str) -> dict | None:
    pmcid = convert_pmid_to_pmcid(pubmed_id)
    if not pmcid:
        return None

    params = {
        "db": "pmc",
        "id": pmcid,
        "retmode": "xml",
        "rettype": "full",
    }
    response = requests.get(PMC_FETCH_URL, params=params)

    if "PMC" not in response.text[:500]:
        return None

    data = xmltodict.parse(response.text)
    try:
        body = data["pmc-articleset"]["article"]["body"]
        sections = body.get("sec", [])
        if isinstance(sections, dict):
            sections = [sections]

        full_text = " ".join(
            sec.get("p", "") if isinstance(sec.get("p", ""), str)
            else " ".join(sec.get("p", []))
            for sec in sections
        )
        return {"text": full_text, "source": f"pmc_{pubmed_id}", "page": 1}
    except (KeyError, TypeError):
        return None


def fetch_papers(query: str, max_results: int = 5) -> list[dict]:
    print(f"Searching PubMed for: {query}")
    ids = search_pubmed(query, max_results)
    print(f"Found {len(ids)} papers")

    papers = []
    for pid in ids:
        full = fetch_pmc_fulltext(pid)
        if full:
            papers.append(full)
            print(f"  ✓ full text fetched: pmc_{pid}")
        else:
            abstract = fetch_abstract(pid)
            if abstract:
                papers.append(abstract)
                print(f"  ~ abstract only: pubmed_{pid}")

    return papers
