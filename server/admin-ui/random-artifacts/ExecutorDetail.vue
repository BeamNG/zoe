<template>
  <v-row>
    <v-expansion-panels>
      <v-expansion-panel>
        <v-expansion-panel-header>
          <v-row>
            <v-col cols="12" class="mb-3">
              <div class="d-flex flex-column flex-md-row align-center mb-2">
                <h2 class="ma-0 mr-3">{{ item.clientData.platform.node }}</h2>
                Zoe {{ item.clientData.ZoeVersion }} / {{ item.clientData.platform.platform }} / ID: {{ id }}
              </div>
            </v-col>
          </v-row>
        </v-expansion-panel-header>
        <v-expansion-panel-content>
          <v-row>
            <v-col cols="12" md="4">
              <v-row>
                <v-col cols="12" class="pt-0">
                  <base-card>
                    <v-card-title class="d-flex justify-space-between">
                      CPU average
                    </v-card-title>
                    <v-card-text>
                      <apexchart
                          type="bar"
                          height="140"
                          :options="cpuChart.chartOptions"
                          :series="cpuChart.series"
                      />
                    </v-card-text>
                  </base-card>
                </v-col>

                <v-col cols="12">
                  <base-card>
                    <v-card-title class="d-flex justify-space-between">
                      Memory
                    </v-card-title>
                    <v-card-text>
                      <div class="text-captions text-uppercase text--disabled">Virtual</div>
                      <apexchart
                          type="bar"
                          height="140"
                          :options="memChart.chartOptions"
                          :series="memChart.series"
                      />
                      <v-divider class="my-3" />
                      <div class="text-captions text-uppercase text--disabled">Swap</div>
                      <apexchart
                          style="padding-top:-48px;"
                          type="bar"
                          height="140"
                          :options="memChart.chartOptions"
                          :series="memChart.series"
                      />
                    </v-card-text>
                  </base-card>
                </v-col>
              </v-row>
            </v-col>

            <v-col cols="12" md="8">
              <base-card>
                <v-card-title class="d-flex justify-space-between">
                  Client Info / Client Data
                </v-card-title>
                <v-card-text>
                  <v-row class="pb-2">
                    <v-col cols="12" class="text-captions text-uppercase text--disabled pb-0">Zoe instance</v-col>
                    <v-col cols="12" md="3" class="details-item d-flex flex-wrap py-1">
                      <div>Client type</div>
                      <div class="font-weight-bold">{{ item.clientData.clientType }}</div>
                    </v-col>
                    <v-col cols="12" md="3" class="details-item d-flex flex-wrap py-1">
                      <div>Zoe version</div>
                      <div class="font-weight-bold">{{ item.clientData.ZoeVersion }}</div>
                    </v-col>
                    <v-col cols="12" md="3" class="details-item d-flex flex-wrap py-1">
                      <div>Binary capable</div>
                      <div class="font-weight-bold">{{ item.clientData.binaryCapable }}</div>
                    </v-col>
                  </v-row>
                  <v-divider class="my-2"></v-divider>
                  <v-row class="pb-2">
                    <v-col cols="12" class="text-captions text-uppercase text--disabled pb-0">Platform</v-col>
                    <v-col cols="12" md="3" class="details-item d-flex flex-wrap py-1">
                      <div>Architecture</div>
                      <div class="font-weight-bold">
                        <div v-for="item in item.clientData.platform.arch" class="font-weight-bold">{{ item }}</div>
                      </div>
                    </v-col>
                    <v-col cols="12" md="3" class="details-item d-flex flex-wrap py-1">
                      <div>Machine</div>
                      <div class="font-weight-bold">{{ item.clientData.platform.machine }}</div>
                    </v-col>
                    <v-col cols="12" md="3" class="details-item d-flex flex-wrap py-1">
                      <div>Platform</div>
                      <div class="font-weight-bold">{{ item.clientData.platform.platform }}</div>
                    </v-col>
                    <v-col cols="12" md="3" class="details-item d-flex flex-wrap py-1">
                      <div>Processor</div>
                      <div class="font-weight-bold">{{ item.clientData.platform.processor }}</div>
                    </v-col>
                  </v-row>
                  <v-divider class="my-2"></v-divider>
                  <v-row class="pb-2">
                    <v-col cols="12" class="text-captions text-uppercase text--disabled pb-0">Python</v-col>
                    <v-col cols="12" md="3" class="details-item d-flex flex-wrap py-1">
                      <div>Python build</div>
                      <div class="font-weight-bold">
                        <div v-for="item in item.clientData.platform.python_build" class="font-weight-bold">{{ item }}</div>
                      </div>
                    </v-col>
                    <v-col cols="12" md="3" class="details-item d-flex flex-wrap py-1">
                      <div>Version</div>
                      <div class="font-weight-bold">{{ item.clientData.platform.python_version }}</div>
                    </v-col>
                    <v-col cols="12" md="3" class="details-item d-flex flex-wrap py-1">
                      <div>Compiler</div>
                      <div class="font-weight-bold">{{ item.clientData.platform.python_compiler }}</div>
                    </v-col>
                    <v-col cols="12" md="3" class="details-item d-flex flex-wrap py-1">
                      <div>Implementation</div>
                      <div class="font-weight-bold">{{ item.clientData.platform.python_implementation }}</div>
                    </v-col>
                  </v-row>
                  <v-divider class="my-2"></v-divider>
                  <v-row class="pb-2">
                    <v-col cols="12" class="text-captions text-uppercase text--disabled pb-0">Operating system</v-col>
                    <v-col cols="12" md="3" class="details-item d-flex flex-wrap py-1">
                      <div>System</div>
                      <div class="font-weight-bold">{{ item.clientData.platform.system }}, {{ item.clientData.platform.release }}</div>
                    </v-col>
                    <v-col cols="12" md="3" class="details-item d-flex flex-wrap py-1">
                      <div>Version</div>
                      <div class="font-weight-bold">{{ item.clientData.platform.version }}</div>
                    </v-col>
                    <v-col v-if="item.clientData.platform.libc_ver" cols="12" md="3" class="details-item d-flex flex-wrap py-1">
                      <div>Libc version</div>
                      <div class="font-weight-bold">
                        <div v-for="item in item.clientData.platform.libc_ver" class="font-weight-bold">{{ item }}</div>
                      </div>
                    </v-col>
                    <v-col v-if="item.clientData.platform.win32_edition" cols="12" md="3" class="details-item d-flex flex-wrap py-1">
                      <div>Edition</div>
                      <div class="font-weight-bold">{{ item.clientData.platform.win32_edition }}</div>
                    </v-col>
                    <v-col v-if="item.clientData.platform.win32_is_iot" cols="12" md="3" class="details-item d-flex flex-wrap py-1">
                      <div>Win32 IoT edition</div>
                      <div class="font-weight-bold">{{ item.clientData.platform.win32_is_iot }}</div>
                    </v-col>
                  </v-row>
                  <v-divider class="my-2"></v-divider>
                  <v-row class="pb-2">
                    <v-col cols="12" class="text-captions text-uppercase text--disabled pb-0">GPU Info</v-col>
                    <v-col cols="12" md="3" class="details-item d-flex flex-wrap py-1">
                      <div>GPU Name</div>
                      <div class="font-weight-bold">
                        <div class="font-weight-bold">{{ item.clientData.platform.gpu_name }}</div>
                      </div>
                    </v-col>
                    <v-col cols="12" md="3" class="details-item d-flex flex-wrap py-1">
                      <div>GPU Load</div>
                      <div class="font-weight-bold">
                        <div class="font-weight-bold">{{ item.clientData.platform.gpu_load }}</div>
                      </div>
                    </v-col>
                    <v-col cols="12" md="3" class="details-item d-flex flex-wrap py-1">
                      <div>GPU Free Memory</div>
                      <div class="font-weight-bold">
                        <div class="font-weight-bold">{{ item.clientData.platform.gpu_free_memory }}Mb</div>
                      </div>
                    </v-col>
                  </v-row>
                </v-card-text>
              </base-card>
            </v-col>

            <v-col cols="12" md="4">
              <base-card>
                <v-card-title>
                  <div>
                    <!-- Server version {{ serverVersion }} -->
                    <v-btn class="ma-2" color="error" @click="triggerClientUpdate">
                      Update client data
                    </v-btn>
                  </div>
                </v-card-title>
              </base-card>
            </v-col>

            <v-col cols="12">
              <v-expansion-panels v-if="item">
                <v-expansion-panel>
                  <v-expansion-panel-header>
                    Raw Data
                  </v-expansion-panel-header>
                  <v-expansion-panel-content>
                    <v-row>
                        <v-col cols="12" md="6" class="py-0">
                          <base-card>
                            <v-card-title>
                              clientStats
                            </v-card-title>
                            <v-card-text style="font-size: 0.8em; font-family: monospace; white-space: pre;">
                              {{ JSON.stringify(item.clientStats, null, 2) }}
                            </v-card-text>
                          </base-card>
                        </v-col>
                        <v-col cols="12" md="6" class="py-0">
                          <base-card>
                            <v-card-title>
                              clientData
                            </v-card-title>
                            <v-card-text style="font-size: 0.8em; font-family: monospace; white-space: pre;">
                              {{ JSON.stringify(item.clientData, null, 2) }}
                            </v-card-text>
                          </base-card>
                        </v-col>
                      </v-row>
                  </v-expansion-panel-content>
                </v-expansion-panel>
              </v-expansion-panels>
              <!-- errors -->
              <span v-else-if="!$bngws.connected">Not connected, please wait...</span>
              <span v-else>Executor does not exist</span>
            </v-col>
          </v-row>
        </v-expansion-panel-content>
      </v-expansion-panel>

      <v-expansion-panel>
        <v-expansion-panel-header>
          <v-row>
            <v-col cols="12" class="mb-3">
              <div class="d-flex flex-column flex-md-row align-center mb-2">
                <h2 class="ma-0 mr-3">Upload job</h2>
                <v-chip class="ma-2" color="green" text-color="white">
                    Finished
                    <v-icon right>
                        mdi-check-bold
                    </v-icon>
                </v-chip>
                <v-chip class="ma-2" color="blue" text-color="white">
                    Running
                    <v-icon right>
                        mdi-progress-clock
                    </v-icon>
                </v-chip>
                <v-chip class="ma-2" color="red" text-color="white">
                    Failed
                    <v-icon right>
                        mdi-alert-octagon
                    </v-icon>
                </v-chip>
              </div>
            </v-col>
          </v-row>
        </v-expansion-panel-header>
        <v-expansion-panel-content>
          <v-row>
            <v-col cols="12" md="4">
              <div style="border-style:solid">
                <input type="file" ref="doc" @change="readFile()" />
              </div>
            </v-col>
          </v-row>
          <v-row>
            <v-simple-table dense>
              <template v-slot:default>
                <thead>
                  <tr>
                    <th class="text-left">Time</th>
                    <th class="text-left">Severity</th>
                    <th class="text-left">Message</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="log in logs" :class="'LOG_' + log.l">
                    <td>{{ parseFloat(log.t).toFixed(2) }}</td>
                    <td>{{log.l}}</td>
                    <td>
                      <div v-if="log.task">
                        {{ log.type }} | {{ log.task.id }} | {{log.task.procState}} | {{ log.task.title }}
                      </div>
                      <div v-else>
                        {{ log.message || log.m }}
                      </div>
                    </td>
                    <!-- TODO FIXME -->
                    <v-tooltip>
                    <pre>{{ JSON.stringify(logs, null, 2) }}</pre>
                    </v-tooltip>
                  </tr>
                </tbody>
              </template>
            </v-simple-table>


          </v-row>
        </v-expansion-panel-content>
      </v-expansion-panel>
    </v-expansion-panels>

  </v-row>
</template>

<script>
export default {
  metaInfo: {
    title: 'Executor'
  },
  data() {
    return {
      id: this.$route.params.id,
      item: null,
      logs: [],
      cpuChart: {
        series: [
          {name: "15min", data: [15]},
          {name: "5min", data: [0.56]},
          {name: "1min", data: [0.1]}],
        chartOptions: {
          chart: {
            type: 'bar',
            height: 200,
            toolbar: {
              show: false,
            }
          },
          plotOptions: {
            bar: {
              horizontal: true,
            }
          },
          tooltip: {
            shared: true,
            intersect: false
          },
          xaxis: {
            show: false,
            showAlways: false,
            categories: ["CPULoad"],
            align: "right",
          },
          yaxis: {
            show: false,
            showAlways: false,
            floating: true,
            align: "right",
          },
        }
      },
      memChart: {
        series: [
          {name: "Used", data: [19876455567]},
          {name: "Busy", data: [4107001856]},
          {name: "Free", data: [64553504768]}],
        chartOptions: {
          chart: {
            type: 'bar',
            height: 200,
            toolbar: {
              show: false,
            },
            stacked: true,
          },
          plotOptions: {
            bar: {
              horizontal: true,
              // dataLabels: {
              //   position: 'bottom',
              //   maxItems: 0,
              //   hideOverflowingLabels: true,
              //   orientation: 'horizontal',
              // },
            },
          },
          tooltip: {
            shared: true,
            intersect: false
          },
          xaxis: {
            show: false,
            showAlways: false,
            categories: ["Memory"],
            tickAmount: 1,
            align: "right",
          },
          yaxis: {
            show: false,
            showAlways: false,
            floating: true,
            tickAmount: 1,
            align: "right",
            max: 96739999999,
          },
        }
      }
    }
  },
  methods: {
    triggerClientUpdate() {
      // TODO
    },
    subscribe() {
      if (!this.item)
        this.item = this.$zoe.executors.find(ex => ex.clientid === this.id);
      if (this.item)
        this.$zoe.send({ type: "subscribe", data: { "targetClient": this.id } });
    },
    readFile() {
      this.file = this.$refs.doc.files[0];
      const reader = new FileReader();
      reader.onloadend = (res) => {
        //console.log(this.file, res.target.result);
        this.logs = []
        this.$zoe.send({ type: "executeFile", data: {targetClient: this.id, filename: this.file.name, filecontent: btoa(res.target.result)} });
      };
      reader.onerror = (err) => console.log(err);
      reader.readAsText(this.file);
    }
  },
  watch: {
    "$bngws.connected" (newVal) {
      if (!newVal)
        this.subscribe();
      else // lost connection
        this.item = null;
    },
    "$zoe.executors" () { // in case if it's a page load
      this.subscribe()
    },
    "$route.params.id" (newVal, oldVal) {
      if (oldVal && this.item)
        this.$zoe.send({ type: "unsubscribe", data: { "targetClient": oldVal } });
      this.id = newVal;
      this.subscribe();
    },
  },
  created() {
    this.subscribe()

    this.$zoe.listen(['log','task_begin', 'task_end', 'task_log'], data => {
      //console.info("Received logs:" , data)
      this.logs.push(data)
    });
  },
  destroyed() {
    if (this.item)
      this.$zoe.send({ type: "unsubscribe", data: { "targetClient": this.id } });
  }
}
</script>
<style lang="scss" scoped>
  .details-item {
    align-content: start;
    & > * {
      flex: 1 0 8em;
      align-self: flex-start;
      word-wrap: break-word;
      &:first-child {
        flex: 0 0 8em;
      }
    }
  }

.LOG_DEBUG { background-color: #b3ffde }
.LOG_INFO { background-color: #74ed94 }
.LOG_WARNING { background-color: #ffbd7a }
.LOG_ERROR { background-color: #ff7a7a }
.LOG_CRITICAL { background-color: #ff4747 }
</style>

