<template>
  <base-card class="files">
    <v-card-title>
      File browser
    </v-card-title>
    <v-row>
      <v-col cols="4">
        <v-list
          shaped
          dense
          no-action
        >
          <v-list-group
            no-action
            v-for="(dir, i) in tree.dirs" :key="dir.name"
            v-model="dir.active"
          >
            <template v-slot:activator>
              <v-list-item-content>
                <v-list-item-title>
                  <v-icon left :color="dir.active ? 'blue' : ''">
                    {{ dir.active ? "mdi-folder-open" : "mdi-folder" }}
                  </v-icon>
                  {{ dir.name + '/' }}
                </v-list-item-title>
              </v-list-item-content>
            </template>
            <v-list-item
              v-for="(file, i) in dir.files"
              :key="file.path"
              prepend-icon="mdi-file"
              :class="path === file.path ? 'v-list-item--active' : ''"
              :to="{ name: 'fileBrowser', params: { path: file.path.split('/') } }"
            >
              <v-list-item-title>
                <v-icon left :color="path === file.path ? 'blue' : ''">
                  {{ path === file.path ? "mdi-file-document" : "mdi-file" }}
                </v-icon>
                {{ file.name }}
              </v-list-item-title>
            </v-list-item>
          </v-list-group>
          <v-list-item
            v-for="(file, i) in tree.files"
            :key="file.path"
            :class="path === file.path ? 'v-list-item--active' : ''"
            :to="{ name: 'fileBrowser', params: { path: [file.path] } }"
          >
            <v-list-item-title>
              <v-icon left :color="path === file.path ? 'blue' : ''">
                {{ path === file.path ? "mdi-file-document" : "mdi-file" }}
              </v-icon>
              {{ file.name }}
            </v-list-item-title>
          </v-list-item>
        </v-list>

      </v-col>
      <v-col cols="8" v-if="path && fileNames.includes(path)">
        <base-card>
          <v-card-title v-text="path"></v-card-title>
          <textarea readonly>{{ files[path] }}</textarea>
        </base-card>
      </v-col>
    </v-row>
  </base-card>
</template>

<script>
export default {
  metaInfo: {
    // title will be injected into parent titleTemplate
    title: "File browser"
  },
  data() {
    return {
      fileNames: [],
      files: {},
      tree: {},
      path: "",
    }
  },
  methods: {
    async loadList() {
      // await for response example:
      // console.log("Files:", await this.$zoe.request({ type: "requestFilesList" }));
      // request with callback example:
      // this.$zoe.request({ type: "requestFilesList" }, data => console.log("Files:", data));
      this.fileNames = Object.keys(
        await this.$zoe.request({ type: "requestFilesList" })
      ).sort((a, b) => a.localeCompare(b, "en", { sensitivity: "base" }));

      // build simple two-level structure
      const tree = {
        dirs: [],
        files: []
      };
      const dirs = [];
      for (let fileName of this.fileNames) {
        if (fileName.indexOf("/") > -1) {
          const dir = fileName.split("/", 1)[0];
          const name = fileName.substring(dir.length + 1);
          let idx = dirs.indexOf(dir);
          if (idx === -1) {
            dirs.push(dir);
            tree.dirs.push({ name: dir, files: [], active: dir === "examples" });
            idx += dirs.length;
          }
          tree.dirs[idx].files.push({ name, path: fileName });
        } else {
          tree.files.push({ name: fileName, path: fileName });
        }
      }
      this.tree = tree;
      // navigate to path if specified
      if (this.path) {
        for (let dir of this.tree.dirs)
          dir.active = this.path.indexOf(dir.name) === 0;
        this.openFile(this.path);
      }
    },
    openFile(fileName) {
      if (!this.files.hasOwnProperty(fileName)) {
        this.$set(this.files, fileName, "<loading>");
        this.$zoe.request(
          { type: "requestFiles", data: [fileName] },
          data => this.$set(this.files, fileName, data.fileData[fileName] || "<no data>")
        );
      }
    }
  },
  watch: {
    "$bngws.connected" (newVal) {
      if (newVal) {
        this.loadList();
      } else { // lost connection
        this.fileNames = [];
        this.files = {};
        this.tree = {};
      }
    },
    "$route.params.path" (newVal) {
      this.path = this.$route.params.path ? newVal.join("/") : newVal;
      if (this.path)
        this.openFile(this.path);
    },
  },
  created() {
    if (this.$route.params.path)
      this.path = Array.isArray(this.$route.params.path) ? this.$route.params.path.join("/") : this.$route.params.path;
    this.loadList();
  }
}
</script>
<style lang="scss" scoped>
.v-list-group__items > .v-list-item {
  padding-left: 3.5em !important;
}
textarea {
  width: 100%;
  height: calc(100vh - 17rem);
  min-height: 30em;
}
</style>
