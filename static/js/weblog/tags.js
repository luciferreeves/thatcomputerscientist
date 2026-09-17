document.addEventListener('DOMContentLoaded', function() {
    var polaroids = document.querySelectorAll('.tags-page .polaroid');
    if (!polaroids.length) return;

    var positions = [
        { x: 0, y: 0 }, { x: 160, y: 30 }, { x: 320, y: 15 }, { x: 480, y: 45 }, { x: 580, y: 20 },
        { x: 80, y: 200 }, { x: 240, y: 220 }, { x: 400, y: 190 }, { x: 560, y: 230 },
        { x: 20, y: 400 }, { x: 180, y: 380 }, { x: 340, y: 420 }, { x: 500, y: 390 }, { x: 580, y: 410 },
        { x: 100, y: 600 }, { x: 260, y: 580 }, { x: 420, y: 620 }, { x: 580, y: 590 },
        { x: 40, y: 800 }, { x: 200, y: 780 }, { x: 360, y: 820 }, { x: 520, y: 790 },
        { x: 120, y: 1000 }, { x: 280, y: 980 }, { x: 440, y: 1020 }, { x: 580, y: 990 },
        { x: 60, y: 1200 }, { x: 220, y: 1180 }, { x: 380, y: 1220 }, { x: 540, y: 1190 }
    ];

    var maxY = 0;
    polaroids.forEach(function(polaroid, i) {
        var pos = positions[i % 30];
        var group = Math.floor(i / 30);
        var seed = Math.sin(456 + i) * 10000 - Math.floor(Math.sin(456 + i) * 10000);
        var finalY = pos.y + group * 1400;

        polaroid.style.position = 'absolute';
        polaroid.style.left = pos.x + 'px';
        polaroid.style.top = finalY + 'px';
        polaroid.style.transform = 'rotate(' + ((seed - 0.5) * 12) + 'deg)';
        polaroid.style.zIndex = Math.floor(seed * 10) + 1 + group * 15;

        maxY = Math.max(maxY, finalY + 240);
    });

    document.querySelector('.tags-page .content-grid').style.minHeight = (maxY + 50) + 'px';
});
