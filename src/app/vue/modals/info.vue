<template>
	<button class="btn btn-secondary btn-sm" type="button" @click="info" v-if="more">More info</button>
	<Teleport to="body">
		<div class="modal fade" id="info" v-if="store.font">
			<div class="modal-dialog modal-dialog-centered modal-lg">
				<div class="modal-content">
					<div class="modal-body">
						<table class="w-100">
							<tr v-if="store.font.description">
								<td>Description</td>
								<td :class="{ 'small': store.font.description.length > 200 }">
									{{ store.font.description }}
								</td>
							</tr>
							<tr v-if="store.font.designer">
								<td>Designer</td>
								<td>
									<a :href="store.font.designerURL" v-if="store.font.designerURL">
										{{ store.font.designer }}
									</a>
									<span v-else>{{ store.font.designer }}</span>
								</td>
							</tr>
							<tr v-if="store.font.manufacturer">
								<td>Manufacturer</td>
								<td>
									<a :href="store.font.vendorURL" v-if="store.font.vendorURL">
										{{ store.font.manufacturer }}
									</a>
									<span v-else>{{ store.font.manufacturer }}</span>
								</td>
							</tr>
							<tr v-if="store.font.copyright">
								<td>Copyright</td>
								<td>{{ store.font.copyright }}</td>
							</tr>
							<tr v-if="store.font.trademark">
								<td>Trademark</td>
								<td>{{ store.font.trademark }}</td>
							</tr>
							<tr v-if="store.font.license">
								<td>license</td>
								<td :class="{ 'small': store.font.license && store.font.license.length > 200 }">
									{{ store.font.license }}
								</td>
							</tr>
						</table>
					</div>
					<div class="modal-footer">
						<button class="btn btn-primary" type="button" data-bs-dismiss="modal">OK</button>
					</div>
				</div>
			</div>
		</div>
	</Teleport>
</template>

<script setup lang="ts">
	import { computed } from "vue";

	import { store } from "../../store";
	import { modal } from "../../utils";

	function info(): void {
		modal("#info").show();
	}

	const more = computed(() => {
		const f = store.font;
		if(!f) return false;
		return f.description || f.designer || f.manufacturer || f.copyright || f.trademark;
	});
</script>
