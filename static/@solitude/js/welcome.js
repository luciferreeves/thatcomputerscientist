Object.defineProperty(Array.prototype, "shuffle", {
  value: function () {
    for (let i = this.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [this[i], this[j]] = [this[j], this[i]];
    }
    return this;
  },
});

const tracks = Object.entries(playlistTracks)
  .map((track) => track[1])
  .shuffle();

const controls = document.querySelector(".controls");
const audio = document.querySelector("#audio");
const trackTitle = document.querySelector("#track-title");
const trackArtist = document.querySelector("#track-artist");
const albumArt = document.querySelector("#album-art");
const minElap = document.querySelector("#min-elap");
const secElap = document.querySelector("#sec-elap");
const minDur = document.querySelector("#min-dur");
const secDur = document.querySelector("#sec-dur");

let currentTrack = 0;

const loadAudio = new Promise((resolve, reject) => {
  audio.addEventListener("canplaythrough", () => {
    resolve(audio);
  });
});

async function playAudio() {
  audio.src = tracks[currentTrack].location;
  const duration = audio.duration;
  audio.play().catch((e) => {
    window.addEventListener(
      "click",
      () => {
        controls.click();
        audio.play();
      },
      { once: true }
    );
  });
  return audio;
}

function pauseAudio() {
  audio.pause();
}

function nextTrack() {
  currentTrack = (currentTrack + 1) % tracks.length;
  audio.currentTime = 0;
  playTrack();
}

function playTrack() {
  const track = tracks[currentTrack];
  trackTitle.textContent = track.title;
  trackArtist.textContent = track.artist;
  albumArt.src = track.cover_art;
  playAudio().then((audio) => {
    audio.addEventListener("ended", nextTrack);
  });
}

function updateIntervals() {
  const duration = audio.duration;
  const currentTime = audio.currentTime;
  const elapsed = Math.floor(currentTime);
  const total = Math.floor(duration);
  const minutesElapsed = Math.floor(elapsed / 60);
  const secondsElapsed = elapsed % 60;
  const minutesTotal = Math.floor(total / 60) || 0;
  const secondsTotal = total % 60 || 0;
  minElap.textContent =
    minutesElapsed < 10 ? `0${minutesElapsed}` : minutesElapsed;
  secElap.textContent =
    secondsElapsed < 10 ? `0${secondsElapsed}` : secondsElapsed;
  minDur.textContent = minutesTotal < 10 ? `0${minutesTotal}` : minutesTotal;
  secDur.textContent = secondsTotal < 10 ? `0${secondsTotal}` : secondsTotal;
}

function togglePlayPause() {
  const buttons = Array.from(this.children);
  let triggeredButton;
  buttons.forEach((button) => {
    if (!button.classList.contains("hidden")) {
      triggeredButton = button;
    }
    button.classList.toggle("hidden");
  });
  signalTrigger(triggeredButton);
}

function signalTrigger(button) {
  const role = button.getAttribute("role");
  switch (role) {
    case "play":
      playAudio();
      break;
    case "pause":
      pauseAudio();
      break;
  }
}

audio.currentTime = 0;
controls.addEventListener("click", togglePlayPause);
audio.addEventListener("timeupdate", updateIntervals);
playTrack();
