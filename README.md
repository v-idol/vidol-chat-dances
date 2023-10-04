# This is the Dance Index of Vidol Chat

[Vidol Chat](https://github.com/v-idol/vidol.chat) accesses [`index.json`](https://github.com/v-idol/vidol-chat-dance/blob/main/index.json) from this repo to show user the list of available dance.

## How to submit dance

If you wish to add an dance onto the index, make an entry in `dance` directory using `dance_template.json`, write a short description then open as a pull request ty!

### Step by step instructions

1. Fork of this repository.

2. Make a copy of `dance_template.json`

3. Fill in the copy and rename it appropriately

4. Move it into `dance` directory

5. Submit a pull request and wait for review.

- dance pull requests targets [`dance branch`](https://github.com/v-idol/vidol-chat-dance/tree/dance), after merge it is automatically assembled and deployed to [`main branch`](https://github.com/v-idol/vidol-chat-dance/tree/main) using GitHub Actions.

- Don't edit the `index.json` directly and don't modify any other files unless you have a special reason.

- The `created` date will be automatically populated after merge.
