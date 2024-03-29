<template>
  <div>
    <button @click="downloadFile">Download File</button>
  </div>
</template>

<script>
export default {
  methods: {
    downloadFile() {
      // Make an API call to get the file data
      fetch('/artifacts', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      })
        .then((response) => {
          // Convert the response to a blob
          return response.blob();
        })
        .then((blob) => {
          // Create a temporary URL for the blob
          const url = URL.createObjectURL(blob);

          // Create a link and click it to download the file
          const link = document.createElement('a');
          link.href = url;
          link.download = 'file.pdf';
          link.click();
        })
        .catch((error) => {
          console.log(error);
        });
    },
  },
};
</script>
