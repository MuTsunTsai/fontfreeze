<template>
	<v-btn color="secondary" size="small" @click="show = true" v-if="more">More info</v-btn>
	<v-dialog v-model="show" width="auto" max-width="1024">
		<v-card v-if="store.font">
			<v-card-text>
				<v-table>
					<tbody>
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
					</tbody>
				</v-table>
			</v-card-text>
			<v-card-actions>
				<v-btn color="primary" @click="show = false">OK</v-btn>
			</v-card-actions>
		</v-card>
	</v-dialog>
</template>

<script setup lang="ts">
	import { computed, shallowRef } from "vue";

	import { store } from "../../store";

	const show = shallowRef(false);

	const more = computed(() => {
		const f = store.font;
		if(!f) return false;
		return f.description || f.designer || f.manufacturer || f.copyright || f.trademark;
	});
</script>

<style scoped>
	.v-table td {
		vertical-align: top !important;
		padding: 4px 16px !important;
	}
</style>
