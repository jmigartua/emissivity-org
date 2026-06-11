#!/usr/bin/env bash
# Downloads the IR-EMPOWER 2024 speaker photos from the frozen legacy
# site into the archive's local assets. Run once, commit the images.
mkdir -p "$(dirname "$0")/../assets/images/ir-empower-2024" && cd "$(dirname "$0")/../assets/images/ir-empower-2024" || exit 1
[ -f "albert-adibekyan.jpg" ] || curl -sSL -o "albert-adibekyan.jpg" "https://dulcet-sundae-44ceba.netlify.app/speakers/albert-adibekyan.jpg" && echo "ok albert-adibekyan"
[ -f "jochen-manara.jpg" ] || curl -sSL -o "jochen-manara.jpg" "https://dulcet-sundae-44ceba.netlify.app/speakers/jochen-manara.jpg" && echo "ok jochen-manara"
[ -f "david-urban.jpg" ] || curl -sSL -o "david-urban.jpg" "https://dulcet-sundae-44ceba.netlify.app/speakers/david-urban.jpg" && echo "ok david-urban"
[ -f "hongyan-mei.jpg" ] || curl -sSL -o "hongyan-mei.jpg" "https://dulcet-sundae-44ceba.netlify.app/speakers/hongyan-mei.jpg" && echo "ok hongyan-mei"
[ -f "leo-gaillard.jpg" ] || curl -sSL -o "leo-gaillard.jpg" "https://dulcet-sundae-44ceba.netlify.app/speakers/leo-gaillard.jpg" && echo "ok leo-gaillard"
[ -f "mireia-sainz-menchon.jpg" ] || curl -sSL -o "mireia-sainz-menchon.jpg" "https://dulcet-sundae-44ceba.netlify.app/speakers/mireia-sainz-menchon.jpg" && echo "ok mireia-sainz-menchon"
[ -f "jon-gabirondo-lopez.jpg" ] || curl -sSL -o "jon-gabirondo-lopez.jpg" "https://dulcet-sundae-44ceba.netlify.app/speakers/jon-gabirondo-lopez.jpg" && echo "ok jon-gabirondo-lopez"
[ -f "matthias-tyslik.jpg" ] || curl -sSL -o "matthias-tyslik.jpg" "https://dulcet-sundae-44ceba.netlify.app/speakers/matthias-tyslik.jpg" && echo "ok matthias-tyslik"
[ -f "lukas-portner.jpg" ] || curl -sSL -o "lukas-portner.jpg" "https://dulcet-sundae-44ceba.netlify.app/speakers/lukas-portner.jpg" && echo "ok lukas-portner"
[ -f "hunter-schonfeld.jpg" ] || curl -sSL -o "hunter-schonfeld.jpg" "https://dulcet-sundae-44ceba.netlify.app/speakers/hunter-schonfeld.jpg" && echo "ok hunter-schonfeld"
[ -f "elisa-sani.jpg" ] || curl -sSL -o "elisa-sani.jpg" "https://dulcet-sundae-44ceba.netlify.app/speakers/elisa-sani.jpg" && echo "ok elisa-sani"
[ -f "zdenek-vesely.jpg" ] || curl -sSL -o "zdenek-vesely.jpg" "https://dulcet-sundae-44ceba.netlify.app/speakers/zdenek-vesely.jpg" && echo "ok zdenek-vesely"
[ -f "julian-gieseler.jpg" ] || curl -sSL -o "julian-gieseler.jpg" "https://dulcet-sundae-44ceba.netlify.app/speakers/julian-gieseler.jpg" && echo "ok julian-gieseler"
[ -f "leire-del-campo.jpg" ] || curl -sSL -o "leire-del-campo.jpg" "https://dulcet-sundae-44ceba.netlify.app/speakers/leire-del-campo.jpg" && echo "ok leire-del-campo"
[ -f "domingos-de-sousa-meneses.jpg" ] || curl -sSL -o "domingos-de-sousa-meneses.jpg" "https://dulcet-sundae-44ceba.netlify.app/speakers/domingos-de-sousa-meneses.jpg" && echo "ok domingos-de-sousa-meneses"
[ -f "nenad-milosevic.jpg" ] || curl -sSL -o "nenad-milosevic.jpg" "https://dulcet-sundae-44ceba.netlify.app/speakers/nenad-milosevic.jpg" && echo "ok nenad-milosevic"
[ -f "tomas-kralik.jpg" ] || curl -sSL -o "tomas-kralik.jpg" "https://dulcet-sundae-44ceba.netlify.app/speakers/tomas-kralik.jpg" && echo "ok tomas-kralik"
[ -f "konstantinos-boboridis.jpg" ] || curl -sSL -o "konstantinos-boboridis.jpg" "https://dulcet-sundae-44ceba.netlify.app/speakers/konstantinos-boboridis.jpg" && echo "ok konstantinos-boboridis"
[ -f "christophe-escape.jpg" ] || curl -sSL -o "christophe-escape.jpg" "https://dulcet-sundae-44ceba.netlify.app/speakers/christophe-escape.jpg" && echo "ok christophe-escape"
[ -f "yannick-le-maoult.jpg" ] || curl -sSL -o "yannick-le-maoult.jpg" "https://dulcet-sundae-44ceba.netlify.app/speakers/yannick-le-maoult.jpg" && echo "ok yannick-le-maoult"
