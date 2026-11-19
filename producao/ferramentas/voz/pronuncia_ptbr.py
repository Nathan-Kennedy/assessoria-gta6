# Reescreve nomes em ingles do jeito que se fala em PT-BR, antes de mandar pro TTS.
import re, sys
DIC = {
    "Miami Vice": "Maiâmi Vaice", "Brickell": "Brikel", "South Beach": "Sáuth Bích", "Overseas Highway": "Ôuver-cíz Ráiuêi", "Seven Mile Bridge": "Séven Máil Brídge", "Henry Flagler": "Rênri Flégler", "Key West": "Quí Uést", "Clewiston": "Clúiston", "Okeechobee": "Oquitchôubi", "Panama City Beach": "Pánama Síti Bích", "Bayside": "Bêissáid", "Port Gellhorn": "Pórt Guélhorn", "Mount Kalaga": "Máunt Kalága", "Scarface": "Iscarfeice", "spring break": "spring brêik", "NPC": "ene pê cê", "Jason": "Djêison", "airboat": "ér bôut", "Art Déco": "Árt Decô", "Homem da Flórida": "Homem da Flórida",
    "GTA 5": "GTA cinco", "GTA 4": "GTA quatro", "Red Dead 2": "Réd Déd dois", "Rob Nelson": "Róbi Nélson", "Nelson": "Nélson", "Davy Jones": "Dêivi Djôuns", "NateTheHate": "Nêit dê Rêit",
    "Brian Heder": "Bráian Rêder", "IGN": "ai djí ên", "Famitsu": "Famítsu", "Kinda Funny": "Kainda Fâni", "Dazed": "Dêizd",
    "Pay 'n' Spray": "Pêi en Sprêi", "Flow Games": "Flôu Gueims", "Shore Court": "Xór Córt", "Ocean Beach": "Ôuxan Bích",
    "Clark Kent": "Clárk Quént", "Franklin": "Frénklin", "PS4": "pê ésse quatro", "minigun": "mini gân",
    "GTA 6": "GTA seis", "GTA VI": "GTA seis",
    "Vice City": "Vaice Síti", "Ocean Drive": "Ôuxan Dráive", "Leonida Keys": "Leonída Quís", "Florida Keys": "Flórida Quís",
    "Grassrivers": "Gráss Rívers", "Everglades": "Évergleids", "Rockstar": "Róquistar",
    "Leonida": "Leonída", "Ctrl C": "Control C", "Ctrl V": "Control V", "Miami": "Maiâmi", "trailer": "trêiler", "uai": "uái",
}
def aplicar(t):
    for k in sorted(DIC, key=len, reverse=True):
        t = re.sub(r"\b%s\b" % re.escape(k), DIC[k], t)
    return t
if __name__ == "__main__":
    src, dst = sys.argv[1:3]
    open(dst, "w", encoding="utf-8").write(aplicar(open(src, encoding="utf-8").read()))
