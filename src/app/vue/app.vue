<template>
	<Dropzone />
	<div class="container py-3 px-sm-2 px-md-3 px-lg-5">
		<div class="mb-3 d-flex justify-content-end" style="gap:1rem">
			<a class="btn btn-secondary btn-sm" href="https://github.com/MuTsunTsai/fontfreeze">📜 User manual</a>
			<a class="btn btn-secondary btn-sm" href="https://github.com/MuTsunTsai/fontfreeze/issues">🐛 Report issue</a>
		</div>
		<div class="card bg-light">
			<div class="card-body">
				<Header />
				<Main />
				<Local />
			</div>
		</div>
		<div class="row justify-content-center mt-3 gx-2 gy-3">
			<div class="col-auto">
				<a href="https://www.buymeacoffee.com/mutsuntsai" target="_blank"><img width="235" height="50"
						 src="https://img.buymeacoffee.com/button-api/?text=Buy me a coffee&emoji=☕&slug=mutsuntsai&button_colour=6f431f&font_colour=ffffff&font_family=Lato&outline_colour=ffffff&coffee_colour=FFDD00&v=1" /></a>
			</div>
			<div class="col-auto">
				<!-- Product Hunt -->
				<a href="https://www.producthunt.com/posts/fontfreeze?utm_source=badge-featured&utm_medium=badge&utm_souce=badge-fontfreeze"
				   target="_blank"><img class="product-hunt" style="width: 235px; height: 50px;" width="235" height="50" /></a>
			</div>
		</div>
	</div>
</template>

<script setup lang="ts">
	import Header from "./header.vue";
	import Dropzone from "./dropzone.vue";
	import Main from "./main.vue";
	import Local from "./modals/local.vue";
</script>
