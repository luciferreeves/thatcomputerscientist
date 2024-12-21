document.querySelectorAll('.anime-card').forEach(card => {
    const hoverCard = card.querySelector('.anime-hover-card');

    card.addEventListener('mouseenter', (e) => {
        positionHoverCard(e, hoverCard);
        hoverCard.style.opacity = '1';
        hoverCard.style.visibility = 'visible';
    });

    card.addEventListener('mousemove', (e) => {
        positionHoverCard(e, hoverCard);
    });

    card.addEventListener('mouseleave', () => {
        hoverCard.style.opacity = '0';
        hoverCard.style.visibility = 'hidden';
    });
});

function positionHoverCard(e, hoverCard) {
    const mouseX = e.clientX;
    const mouseY = e.clientY;
    const viewportWidth = window.innerWidth;
    const viewportHeight = window.innerHeight;
    const cardWidth = 400;
    const cardHeight = hoverCard.offsetHeight;

    // Calculate position, keeping card within viewport
    let left = mouseX + 20; // 20px offset from cursor
    let top = mouseY + 20;

    // Adjust if card would overflow right side
    if (left + cardWidth > viewportWidth) {
        left = mouseX - cardWidth - 20;
    }

    // Adjust if card would overflow bottom
    if (top + cardHeight > viewportHeight) {
        top = mouseY - cardHeight - 20;
    }

    // Apply position
    hoverCard.style.left = `${left}px`;
    hoverCard.style.top = `${top}px`;
}