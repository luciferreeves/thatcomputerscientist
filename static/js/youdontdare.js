let FACounter = 0
let timesFA = document.getElementById('timesFA')
const FUpMessages = (FACounter) => {
    if (FACounter === 0) return "Hey! Back off, fuckface!";
    if (FACounter === 4) return "Don't you fucking dare, you little shit!";
    if (FACounter === 9) return "Haven't you fucked around enough, you absolute wankstain?";
    if (FACounter === 14) return "Aren't you a relentless cockwomble? Fuck off already!";
    if (FACounter === 19) return "Fucking hell, you're like herpes - just won't go away!";
    if (FACounter === 24) return "I'm done. Go play in traffic, you waste of oxygen.";
    if (FACounter === 41) return "Congrats, you've found the meaning of life: being a colossal pain in my ass!";
    if (FACounter === 49) return "Half a hundred clicks? Did your parents not hug you enough?";
    if (FACounter === 68) return "Nice. Now go get laid for real, you horny bastard.";
    if (FACounter === 99) return "Triple digits? You're a special kind of fucked up, aren't you?";
    if (FACounter === 419) return "Blaze it and fuck off, you stoner dipshit.";
    if (FACounter % 1000 === 999) return "A thousand clicks? I hope your finger falls off, you absolute lunatic!";
    if (FACounter % 500 === 499) return "Jesus fucking Christ, get a life or I'll find one for you in a dumpster!";
    if (FACounter % 100 === 99) return "Another hundred? Your therapist is getting rich off your issues!";
    if (FACounter > 4999) return "Keep clicking, fuckface. I'm sure it'll fill the void in your pathetic life.";
}

function dontYouDare(event) {
    if (timesFA.parentElement.style.display === 'none') {
        timesFA.parentElement.style.display = 'block'
    }

    const previousFAButton = document.getElementById('FAButton')
    if (previousFAButton) {
        document.body.removeChild(previousFAButton)
    }
    const FAButton = document.createElement('div')
    FAButton.id = 'FAButton'
    FAButton.textContent = FUpMessages(FACounter)

    if (FAButton.textContent) {
        applyStyles(event.clientX, event.clientY, FAButton)
        document.body.appendChild(FAButton)
    }
    FACounter += 1
    timesFA.innerText = FACounter
    setTimeout(() => {
        FAButton.style.opacity = 0
        setTimeout(() => {
            try {
                document.body.removeChild(FAButton)
            } catch {
                // pass
            }
        }, 100)
    }, 6000)
}

function applyStyles(x, y, container) {
    container.style.position = 'absolute'
    container.style.top = `${y}px`
    container.style.left = `${x}px`
    container.style.fontSize = '8px'
    container.style.userSelect = 'none'
    container.style.transition = 'opacity 0.5s ease-in-out'
    container.style.textShadow = '0 0 2px #e014df, 0 0 4px #e014df, 0 0 6px #e014df, 0 0 10px #ff00ff, 0 0 14px #ff00ff';
    container.style.color = '#ffffff';
    container.style.backgroundColor = '#8a0885';
    container.style.padding = '4px 8px';
    container.style.border = '1px solid #e014df';
    container.style.borderRadius = '2px';
    container.style.fontWeight = 'bold';
    container.style.zIndex = 1
}

function leaveWebsite() {
    const question = 'Ah, the choice of cowardice! Even trying to click on the disabled button. Let me humour you for once! Are you sure you want to leave?'

    if (confirm(question)) {
        alert('Mentally Weak Coward!')
    }
}

function stopAndPlayPresentDay() {
    const audio = document.getElementById('presentDayAudio')
    audio.currentTime = 0
    audio.play()
}
