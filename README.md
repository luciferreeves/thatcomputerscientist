# [ThatComputerScientist](https://thatcomputerscientist.com)

![GitHub Workflow Status](https://img.shields.io/github/workflow/status/luciferreeves/thatcomputerscientist/Fly%20Deploy?color=%232088FF&label=deployment&logo=github%20actions&logoColor=white&style=for-the-badge)
![GitHub Sponsors](https://img.shields.io/github/sponsors/luciferreeves?color=%23EA4AAA&logo=GitHub%20Sponsors&logoColor=white&style=for-the-badge)
![GitHub](https://img.shields.io/github/license/luciferreeves/thatcomputerscientist?color=%233DA639&logo=Open%20Source%20Initiative&logoColor=white&style=for-the-badge)
![Lines of code](https://img.shields.io/tokei/lines/github/luciferreeves/thatcomputerscientist?color=%23007ACC&label=lines%20of%20code&logo=Visual%20Studio%20Code&style=for-the-badge)

This repository contains the source code for my personal website which is available at [thatcomputerscientist.com](https://thatcomputerscientist.com) — a retro-looking open-collaboration blog about computer science, statistics, mathematics, programming, and more.

The website is currently in development, but I hope to release it in the future. This entire repository is open-source, and is licensed under the [MIT license](LICENSE.md). More information about the MIT license can be found [here](https://opensource.org/licenses/MIT).

If you would like to contribute to the website, please see the [contributing guide](#contributing).

## Screenshot

Below is the screenshot of how the website looks like right now. This screenshot is being updated programatically by [That Computer Scientist's Screenshot API](https://api.thatcomputerscientist.com/screenshot), and will update as I push more changes to the repository.

![Screenshot](https://api.thatcomputerscientist.com/screenshot?random=0.9081680163471533)

## Cloning, Installing, and Running

This project is built using [Node.js](https://nodejs.org) and utilizes the [Express.js](https://expressjs.com) framework. The website is deployed using [Fly.io](https://fly.io) — Please see [Deployment Instructions](#deployment-instructions) for more information on deployment process.

In order to run the project locally, create a [fork](https://github.com/luciferreeves/thatcomputerscientist/fork) of the repository. Then, clone the fork.

```bash
git clone https://github.com/<username>/<fork>.git
```

Inside the cloned repository, run the following command to install the dependencies:

```bash
npm install
```

Then, run the following command to start the development server:

```bash
npm run dev
```

Open [localhost:3000](http://localhost:3000) in your browser to view the website. Please note that the project also utilizes subdomains. As for the lack of subdomain support on the **_localhost_** page, you can open [vcap.me:3000](https://vcap.me:3000) in your browser alternatively. If you wish to navigate to a subdomain, you can use [&lt;subdomain>.vcap.me:3000](https://<subdomain>.vcap.me:3000) in your browser.

## Deployment Instructions

The website uses [Fly.io](https://fly.io) as its deployment platform. If you would like to follow the deployment process in detail, please see [Build, Deploy & Run a Node Application](https://fly.io/docs/getting-started/node/) guide from the official [Fly.io Docs](https://fly.io/docs).

### Installing flyctl on your machine

The first step is to install the flyctl CLI tool on your machine. Installation instructions could vary based on your operating system. I am taking this from the [Installing flyctl](https://fly.io/docs/getting-started/installing-flyctl/) guide.

> It is recommeded to follow the guide for the latest installation instructions.

<details>
    <summary>macOS</summary>
    <p>If you have the <a href="https://brew.sh/">Homebrew</a> package manager installed, flyctl can be installed by running:</p>
    <pre><code>brew install flyctl</code></pre>
    <p>If not, you can run the install script:</p>
    <pre><code>curl -L https://fly.io/install.sh | sh</code></pre>
</details>

<details>
    <summary>Linux</summary>
    <p>Run the install script:</p>
    <pre><code>curl -L https://fly.io/install.sh | sh</code></pre>
</details>

<details>
    <summary>Windows</summary>
    <p>Run the Powershell install script:</p>
    <pre><code>iwr https://fly.io/install.ps1 -useb | iex</code></pre>
</details>
<br>

### Signup or Login
Next, Create an account with `flyctl auth signup` or login with `flyctl auth login`.

### Create a configuration and deploy to fly.io.
Finally, run `flyctl launch` to create, configure, and deploy a new application. Please note that this command creates a [fly.toml](fly.toml) configuration specific to your account, so you would need to **DELETE** the file before running the command.
    
```bash
rm fly.toml
flyctl launch
```

### Status of the deployment
The status of the deployment can be viewed by running `flyctl status`. You can also open your deployed website by running `flyctl open` from the directory where you cloned the repository.

### Deploying Changes
After you have made changes to the source code, you can deploy them by running `flyctl deploy`.

### Automatically Deploying Changes using GitHub Actions
If you would like to automatically deploy changes to your website when you push to the repository, you can use the [GitHub Actions](
https://help.github.com/en/actions/configuring-and-managing-workflows/using-github-actions) workflow. First, you would need to create a new authentication token for your repository. You can do this by running the following command:

```bash
flyctl auth token
```

Then, you would need to add the token to your repository's settings. 
Go to your repository settings, then select "Secrets" from the sidebar, and create a secret called `FLY_API_TOKEN` with the value of the token you just created.

Then, you would need to create [.github/workflows/main.yml](.github/workflows/main.yml) file. You can take a look at the file present in this repository for reference or copy and paste the following contents into the file:

```yaml
name: Fly Deploy
on: [push]
env:
  FLY_API_TOKEN: ${{ secrets.FLY_API_TOKEN }}
jobs:
  deploy:
      name: Deploy app
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v2
        - uses: superfly/flyctl-actions/setup-flyctl@master
        - run: flyctl deploy --remote-only
```
    
Then, you can push your changes to the repository and the workflow will automatically deploy your changes.

## Contributing

There are various ways to contribute to the project. Here is a short summary of the ways you can contribute. A detailed contributing guide is available in the [CONTRIBUTING.md](CONTRIBUTING.md) file.

### 🐞 Found a bug?
You can report a bug by [opening an issue on GitHub](https://github.com/luciferreeves/thatcomputerscientist/issues). Please include a detailed description of the bug and a screenshot of the error. You can also provide additional information about your system and browser. Make sure to use the [Bug Report](https://github.com/luciferreeves/thatcomputerscientist/issues/new?assignees=&labels=bug&template=bug_report.md&title=%5BBUG%5D) template for your issue.

### 📝 Suggestions for improvement?
You can suggest improvements to the project by [opening an issue on GitHub](https://github.com/luciferreeves/thatcomputerscientist/issues). Please include a detailed description of the improvement and a screenshot of the improvement. Make sure to use the [Feature Request](https://github.com/luciferreeves/thatcomputerscientist/issues/new?assignees=&labels=enhancement&template=feature_request.md&title=%5BENHANCEMENT%5D) template for your issue.

### 🔨 Tinkered with the code? Submit a pull request.
If you made any changes to the source code and want it to be included in the next release, you can [submit a pull request on GitHub](https://github.com/luciferreeves/thatcomputerscientist/pulls). Please include a detailed description of the changes and a screenshot of the changes.

