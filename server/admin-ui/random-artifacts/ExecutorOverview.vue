<template>
  <v-row>
    <v-col cols="12">
      <base-card>
        <v-card-title class="d-flex justify-space-between">
          <div class="card-title ma-0 flex-grow-1" >Executors</div>
          <v-text-field
            v-model="search"
            append-outer-icon="mdi-magnify"
            label="Search"
            single-line
            hide-details
            clearable
            filled
            dense
            class="flex-grow-0"
          ></v-text-field>
        </v-card-title>
        <v-card-text>
          <v-data-table
            class="elevation-1 table-one"
            v-model="selected"
            :search="search"
            :headers="headers"
            :items="$zoe.executors"
            :footer-props="{
              itemsPerPageOptions:[10,20,30,-1]
            }"
            :items-per-page="30"
            item-key="clientid"
            :expanded="details"
            @click:row="openExecutorDetails"
            multi-sort
          >

            <template v-slot:item.platform="{ item }">
              <div v-if="item.clientData">
                Zoe {{ item.clientData.ZoeVersion }}
                <v-tooltip right v-if="item.clientData.platform.platform">
                  <template v-slot:activator="{on, attrs}">
                    <v-icon v-on="on" v-bind="attrs" color="blue">
                      mdi-{{ item.clientData.platform.platform.toLowerCase().indexOf("windows") === 0 ? "microsoft-windows" : /* microsoft-windows microsoft-windows-classic */
                        item.clientData.platform.platform.toLowerCase().indexOf("linux") === 0 ? "linux" : /* linux penguin */
                        "crosshairs-question" }}
                    </v-icon>
                  </template>
                  <span>{{ item.clientData.platform.platform }}</span>
                </v-tooltip>
                <v-tooltip right>
                  <template v-slot:activator="{on, attrs}">
                    <v-icon v-on="on" v-bind="attrs" small :color="item.clientData.autoupdate ? 'green' : 'grey'">
                      mdi-{{ item.clientData.autoupdate ? "sync" : "sync-off" }}
                    </v-icon>
                  </template>
                  <span>Auto-update {{ item.clientData.autoupdate ? "enabled" : "disabled" }}</span>
                </v-tooltip>
              </div>
            </template>

            <template v-slot:item.stats="{ item }">
              <v-row v-if="item.clientStats">
                <v-col cols="auto">
                  <v-tooltip right>
                    <template v-slot:activator="{on, attrs}">
                      <span v-on="on" v-bind="attrs" class="center">
                        <v-icon color="deep-orange accent-4">mdi-gauge</v-icon>
                        {{ (item.clientStats.cpu_loadavg[0]).toFixed(2) }}
                      </span>
                    </template>
                    <span>System load: {{ (item.clientStats.cpu_loadavg[0]).toFixed(2) }}</span>
                  </v-tooltip>
                </v-col>
                <v-col cols="auto">
                  <v-tooltip right>
                    <template v-slot:activator="{on, attrs}">
                      <span v-on="on" v-bind="attrs" class="center">
                        <v-icon color="teal">mdi-memory</v-icon>
                        {{ (item.clientStats.cpu_freq.current / 1000).toFixed(2) }} GHz
                      </span>
                    </template>
                    <span>CPU speed: {{ (item.clientStats.cpu_freq.current / 1000).toFixed(2) }} GHz</span>
                  </v-tooltip>
                </v-col>
                <v-col cols="auto">
                  <v-tooltip right>
                    <template v-slot:activator="{on, attrs}">
                      <span v-on="on" v-bind="attrs" class="center">
                        <v-icon color="indigo">mdi-database</v-icon>
                        {{ item.clientStats.memory_virtual.percent }}%
                      </span>
                    </template>
                    <span>RAM occupied: {{ item.clientStats.memory_virtual.percent }}%</span>
                  </v-tooltip>
                </v-col>
                <v-col cols="auto">
                  <v-tooltip right>
                    <template v-slot:activator="{on, attrs}">
                      <span v-on="on" v-bind="attrs" class="center">
                        <v-icon color="teal">mdi-expansion-card</v-icon>
                        {{ item.clientData.platform.gpu_load }}
                      </span>
                    </template>
                    <span>GPU Load: {{ item.clientData.platform.gpu_load }}</span>
                  </v-tooltip>
                </v-col>
              </v-row>
              <div v-else class="center">
                <v-icon color="#cfd8dc">mdi-help-rhombus</v-icon>
              </div>
            </template>

            <template v-slot:item.clientStats.memory_virtual.percent="{ item }">
            </template>

            <template v-slot:item.action="{item}">
              <div class="d-flex" @click.stop>
                <v-tooltip top>
                  <template v-slot:activator="{on, attrs}">
                    <v-btn
                      color="success"
                      dark
                      v-bind="attrs"
                      v-on="on"
                      icon
                    >
                      <v-icon>mdi-pencil-box-outline</v-icon>
                    </v-btn>
                  </template>
                  <span>Edit</span>
                </v-tooltip>
                <v-tooltip top>
                  <template v-slot:activator="{on, attrs}">
                    <v-btn
                      color="danger"
                      dark
                      v-bind="attrs"
                      v-on="on"
                      icon
                    >
                      <v-icon>mdi-trash-can-outline</v-icon>
                    </v-btn>
                  </template>
                  <span>Delete</span>
                </v-tooltip>
              </div>
            </template>

            <template v-slot:item.badge="{item}">
              <template v-if="item.badge === 'Active'">
                <v-chip
                  class=""
                  color="success"
                  label
                  small
                  text-color="white"
                >
                  <v-icon small left>mdi-check</v-icon>
                  {{ item.badge }}
                </v-chip>
              </template>
              <template v-else>
                <v-chip
                  class=""
                  color="danger"
                  label
                  small
                  text-color="white"
                >
                  <v-icon small left>mdi-close</v-icon>
                  {{ item.badge }}
                </v-chip>
              </template>
            </template>

          </v-data-table>
          <v-divider class="mt-3"></v-divider>
          <!-- Server version {{ serverVersion }} -->
          <v-btn class="my-2" color="primary" @click="triggerClientUpdates">
            Update all
          </v-btn>
        </v-card-text>
      </base-card>
    </v-col>
  </v-row>
</template>

<script>
export default {
  metaInfo: {
    // title will be injected into parent titleTemplate
    title: 'Executors'
  },
  data() {
    return {
      search: '',
      selected: [],
      headers: [
        { text: 'Node', value: 'clientData.platform.node' },
        {text: 'Platform', value: 'platform'},
        {text: 'Stats', value: 'stats'},
        {text: 'Action', value: 'action'},
      ],
      details: [],
    }
  },
  methods: {
    sendMessage(message) {
      this.$bngws.send(message);
    },
    triggerClientUpdates() {
      this.$bngws.send({ type: "updateAllClients" });
    },
    openExecutorDetails(itm) {
      this.$router.push({ name: "executorDetail", params: { id: itm.clientid } });
    }
  },
  created() {
    this.$zoe.refresh(); // force refresh, yet this is not necessary since data gets updated in a background
    // see plugins/ws-bng.js
  }
}
</script>
<style lang="scss" scoped>
::v-deep .table-one {
  thead.v-data-table-header {
    tr {
      &:hover {
        background-color: #f2f3f8;
      }
      th {
        span {
          font-size: 16px;
          color: #304156;
        }
      }
    }
    tr {
      td {
        padding-bottom: 20px;
        padding-top: 20px;
      }
    }
  }
  tbody {
    tr {
      &:hover {
        background-color: #f2f3f8 !important;
      }
    }
  }
}

.center {
  text-align: center;
}
</style>
