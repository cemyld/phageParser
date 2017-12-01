import re


class Phage:
    SUPPORTED_DATABASES = {
        # European Nucleotide Archive phage database
        "ENA": r"^gi\|[0-9]+\|ref\|([^\|]+)\|\ ([^,]+)[^$]*$",

        # National Center for Biotechnology Information phage database
        "NCBI": r"^ENA\|([^\|]+)\|[^\ ]+\ ([^,]+)[^$]*$",

        # Actinobacteriophage Database
        "AD": r"^([^\ ]+)\ [^,]*,[^,]*,\ Cluster\ ([^$]+)$"
    }

    def __init__(self, raw_text, phage_finder):
        self.raw = raw_text.strip()
        self.refseq = None
        self.name = None
        self.db = None
        self._parse_phage(raw_text, phage_finder)

    def _parse_phage(self, raw_text, phage_finder):
        for db, regex in Phage.SUPPORTED_DATABASES.items():
            match = re.search(regex, raw_text)
            if match is not None:
                if db is not "AD":
                    self.name = match.group(2)
                    self.refseq = match.group(1)
                else:
                    short_name = match.group(1)
                    cluster = match.group(2)
                    self.name = "Mycobacteriophage " + short_name
                    self.refseq = phage_finder.find_by_phage(short_name,
                                                             cluster)
                self.db = db
