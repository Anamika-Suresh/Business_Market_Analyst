from tools.founder_scraper import extract_founders_from_html

HTML_JSON_LD_FIXTURE = """
<!DOCTYPE html>
<html>
<head>
  <title>About Us | SafeAI Labs</title>
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "Organization",
    "name": "SafeAI Labs",
    "url": "https://safeai.example.com",
    "founder": [
      {
        "@type": "Person",
        "name": "Alex Mercer",
        "jobTitle": "Co-Founder & CEO",
        "sameAs": "https://www.linkedin.com/in/alexmercer-ai",
        "description": "Former AI researcher leading alignment."
      },
      {
        "@type": "Person",
        "name": "Elena Rostova",
        "jobTitle": "Co-Founder & Chief Scientist",
        "sameAs": "https://www.linkedin.com/in/elena-rostova",
        "description": "Pioneered neural architecture methods."
      }
    ]
  }
  </script>
</head>
<body>
  <h1>SafeAI Labs Leadership</h1>
</body>
</html>
"""

HTML_SEMANTIC_CARDS_FIXTURE = """
<!DOCTYPE html>
<html>
<body>
  <section class="leadership-section">
    <div class="team-member">
      <h3 class="name">Sarah Connor</h3>
      <p class="role">Chief Executive Officer & Founder</p>
      <p class="bio">Leading systems resilience and autonomous safety.</p>
      <a href="https://www.linkedin.com/in/sarah-connor-ceo">LinkedIn Profile</a>
    </div>
    <div class="team-member">
      <h3 class="name">Marcus Wright</h3>
      <p class="role">Chief Technology Officer</p>
      <p class="bio">Infrastructure and distributed training architect.</p>
    </div>
    <div class="team-member">
      <h3 class="name">Junior Intern</h3>
      <p class="role">Marketing Intern</p>
    </div>
  </section>
</body>
</html>
"""

def test_extract_founders_from_json_ld():
    execs = extract_founders_from_html(HTML_JSON_LD_FIXTURE, source_url="https://safeai.example.com")
    assert len(execs) == 2
    alex = next(e for e in execs if e.name == "Alex Mercer")
    assert alex.title == "Co-Founder & CEO"
    assert alex.is_founder is True
    assert alex.linkedin_url == "https://www.linkedin.com/in/alexmercer-ai"
    assert alex.verified is True

    elena = next(e for e in execs if e.name == "Elena Rostova")
    assert elena.title == "Co-Founder & Chief Scientist"
    assert elena.is_founder is True

def test_extract_founders_from_semantic_cards():
    execs = extract_founders_from_html(HTML_SEMANTIC_CARDS_FIXTURE, source_url="https://cyberdyne.example.com")
    # Sarah (Founder/CEO) and Marcus (CTO) should be extracted; Junior Intern ignored
    assert len(execs) == 2
    names = [e.name for e in execs]
    assert "Sarah Connor" in names
    assert "Marcus Wright" in names
    assert "Junior Intern" not in names

    sarah = next(e for e in execs if e.name == "Sarah Connor")
    assert sarah.is_founder is True
    assert sarah.linkedin_url == "https://www.linkedin.com/in/sarah-connor-ceo"

def test_extract_founders_empty_or_no_founders():
    html = "<html><body><p>Just some plain blog post text.</p></body></html>"
    execs = extract_founders_from_html(html)
    assert execs == []
