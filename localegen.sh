#!/bin/bash

# Colors
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
RED='\033[0;31m'
NC='\033[0m' # No Color
BOLD='\033[1m'

clear

# ASCII Art
echo -e "${CYAN} 
 ████████╗██████╗  █████╗ ███╗   ██╗███████╗██╗      █████╗ ████████╗███████╗
 ╚══██╔══╝██╔══██╗██╔══██╗████╗  ██║██╔════╝██║     ██╔══██╗╚══██╔══╝██╔════╝
    ██║   ██████╔╝███████║██╔██╗ ██║███████╗██║     ███████║   ██║   █████╗  
    ██║   ██╔══██╗██╔══██║██║╚██╗██║╚════██║██║     ██╔══██║   ██║   ██╔══╝  
    ██║   ██║  ██║██║  ██║██║ ╚████║███████║███████╗██║  ██║   ██║   ███████╗
    ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝╚══════╝╚══════╝╚═╝  ╚═╝   ╚═╝   ╚══════╝
                                                                            ${NC}"

echo -e "${PURPLE}   ᕕ(⌐■_■)ᕗ ${GREEN}Locale generation tool ${YELLOW}for Japanese templates${NC}\n"

LANG_CODE="ja"

generate_messages() {
  echo -e "\n${BOLD}${YELLOW}Generating translation messages for ${LANG_CODE} (HTML templates only)...${NC}\n"
  
  python manage.py makemessages -l ${LANG_CODE} -e html \
    --ignore="templates.old/*" \
    --ignore="venv/*"
  
  echo -e "\n${GREEN}✓ Translation message files successfully generated!${NC}"
  echo -e "${BLUE}You can now edit the .po files in locale/${LANG_CODE}/LC_MESSAGES/${NC}\n"
}

compile_messages() {
  echo -e "\n${BOLD}${YELLOW}Compiling translation messages for ${LANG_CODE}...${NC}\n"
  
  if [[ ! -d "locale/${LANG_CODE}/LC_MESSAGES" ]]; then
    echo -e "${RED}Error: Could not find locale/${LANG_CODE}/LC_MESSAGES directory.${NC}"
    exit 1
  fi

  cd locale/${LANG_CODE}/LC_MESSAGES || exit 1
  
  if [[ ! -f "django.po" ]]; then
    echo -e "${RED}Error: Could not find django.po file in locale/${LANG_CODE}/LC_MESSAGES directory.${NC}"
    echo -e "${YELLOW}Tip: Run the generate option first to create translation files.${NC}"
    cd - > /dev/null
    exit 1
  fi
  
  echo -e "${BLUE}Compiling django.po...${NC}"
  if msgfmt django.po -o django.mo; then
    echo -e "${GREEN}✓ Compiled django.mo successfully.${NC}"
  else
    echo -e "${RED}Error: Failed to compile django.po${NC}"
    cd - > /dev/null
    exit 1
  fi
  
  cd - > /dev/null
  echo -e "\n${GREEN}✓ Translation messages compilation complete!${NC}\n"
}

echo -e "${BOLD}${CYAN}What do you want to do?${NC}"
echo -e "  ${GREEN}g${NC} - Generate translation messages"
echo -e "  ${BLUE}c${NC} - Compile translation messages"
echo -n -e "${YELLOW}Choose an option ${NC}[${GREEN}g${NC}]: "
read -n 1 action
echo ""

case "$action" in
  "g"|"")
    generate_messages
    ;;
  "c")
    compile_messages
    ;;
  *)
    echo -e "\n${RED}Error: Invalid option. Use 'g' for generate or 'c' for compile.${NC}"
    exit 1
    ;;
esac