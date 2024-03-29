<template>
  <v-row>
    <v-col cols="12" md="3">
      <v-treeview
        v-model="tree"
        :open="initiallyOpen"
        :items="tasks['/'].tree"
        activatable
        item-key="name"
        open-on-click
      >
        <template v-slot:prepend="{ item, open }">
          <v-icon v-if="!item.icon">
            {{ open ? 'mdi-folder-open' : 'mdi-folder' }}
          </v-icon>
          <v-icon v-else>
            {{ iconShortcuts[item.icon] }}
          </v-icon>
        </template>
      </v-treeview>
    </v-col>
    <v-divider></v-divider>
    <v-col cols="12" md="9">
      <v-data-table
        :headers="taskHeaders"
        :items="tasks[selectedTask].events"
        :single-expand="singleExpand"
        :expanded.sync="expanded"
        item-key="id"
        show-expand
        class="elevation-1"
      >
        <template v-slot:item.created_at="{ item }">
          <span>{{ new Date(item.created_at).toLocaleString() }}</span>
        </template>
        <template v-slot:expanded-item="{ headers, item }">
          <td :colspan="headers.length">
            More info about {{ item.name }}
          </td>
        </template>
      </v-data-table>
    </v-col>
  </v-row>
</template>

<script>
export default {
  props: {
    tasks: {},
  },
  data: () => ({
    selectedTask: '/',
    initiallyOpen: ['public'],
    iconShortcuts: {
      html: 'mdi-language-html5',
      js: 'mdi-nodejs',
      json: 'mdi-code-json',
      md: 'mdi-language-markdown',
      pdf: 'mdi-file-pdf',
      png: 'mdi-file-image',
      txt: 'mdi-file-document-outline',
      xls: 'mdi-file-excel',
    },
    tree: [],
    items: [
      {
        name: '.git',
      },
      {
        name: 'node_modules',
      },
      {
        name: 'public',
        children: [
          {
            name: 'static',
            children: [{
              name: 'logo.png',
              icon: 'png',
            }],
          },
          {
            name: 'favicon.ico',
            icon: 'png',
          },
          {
            name: 'index.html',
            icon: 'html',
          },
        ],
      },
      {
        name: '.gitignore',
        icon: 'txt',
      },
      {
        name: 'babel.config.js',
        icon: 'js',
      },
      {
        name: 'package.json',
        icon: 'json',
      },
      {
        name: 'README.md',
        icon: 'md',
      },
      {
        name: 'vue.config.js',
        icon: 'js',
      },
      {
        name: 'yarn.lock',
        icon: 'txt',
      },
    ],
    expanded: [],
    singleExpand: true,
    taskHeaders: [
      { text: '', value: 'data-table-expand' },
      {
        text: 'Time',
        align: 'start',
        sortable: false,
        value: 'created_at',
      },
      { text: 'Message', value: 'message' },
    ],
  }),
}
</script>
<style lang="scss" scoped>
.LOG_DEBUG { background-color: #b3ffde }
.LOG_INFO { background-color: #74ed94 }
.LOG_WARNING { background-color: #ffbd7a }
.LOG_ERROR { background-color: #ff7a7a }
.LOG_CRITICAL { background-color: #ff4747 }
</style>
