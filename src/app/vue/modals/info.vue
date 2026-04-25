<template>
	<v-btn
		v-if="more"
		color="secondary"
		size="small"
		@click="show = true"
	>
		{{ $t("info.moreInfo") }}
	</v-btn>
	<v-dialog v-model="show" width="auto" max-width="1024">
		<v-card v-if="store.font">
			<v-card-text>
				<v-table>
					<tbody>
						<tr v-if="store.font.description">
							<td class="d-none d-sm-table-cell">{{ $t("info.description") }}</td>
							<td :class="{ 'small': store.font.description.length > 200 }">
								<h6 class="d-block d-sm-none text-h6 text-info">{{ $t("info.description") }}</h6>
								{{ store.font.description }}
							</td>
						</tr>
						<tr v-if="store.font.designer">
							<td class="d-none d-sm-table-cell">{{ $t("info.designer") }}</td>
							<td>
								<h6 class="d-block d-sm-none text-h6 text-info">{{ $t("info.designer") }}</h6>
								<a v-if="store.font.designerURL" :href="store.font.designerURL">
									{{ store.font.designer }}
								</a>
								<span v-else>{{ store.font.designer }}</span>
							</td>
						</tr>
						<tr v-if="store.font.manufacturer">
							<td class="d-none d-sm-table-cell">{{ $t("info.manufacturer") }}</td>
							<td>
								<h6 class="d-block d-sm-none text-h6 text-info">{{ $t("info.manufacturer") }}</h6>
								<a v-if="store.font.vendorURL" :href="store.font.vendorURL">
									{{ store.font.manufacturer }}
								</a>
								<span v-else>{{ store.font.manufacturer }}</span>
							</td>
						</tr>
						<tr v-if="store.font.copyright">
							<td class="d-none d-sm-table-cell">{{ $t("info.copyright") }}</td>
							<td>
								<h6 class="d-block d-sm-none text-h6 text-info">{{ $t("info.copyright") }}</h6>
								<div>{{ store.font.copyright }}</div>
							</td>
						</tr>
						<tr v-if="store.font.trademark">
							<td class="d-none d-sm-table-cell">{{ $t("info.trademark") }}</td>
							<td>
								<h6 class="d-block d-sm-none text-h6 text-info">{{ $t("info.trademark") }}</h6>
								<div>{{ store.font.trademark }}</div>
							</td>
						</tr>
						<tr v-if="store.font.license">
							<td class="d-none d-sm-table-cell">{{ $t("info.license") }}</td>
							<td>
								<h6 class="d-block d-sm-none text-h6 text-info">{{ $t("info.license") }}</h6>
								<div :class="{ 'text-body-2': store.font.license && store.font.license.length > 200 }">
									{{
										store.font.license }}
								</div>
							</td>
						</tr>
					</tbody>
				</v-table>
			</v-card-text>
			<v-card-actions>
				<v-btn color="primary" @click="show = false">{{ $t("alert.ok") }}</v-btn>
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

<style scoped lang="scss">
	.v-table td {
		vertical-align: top !important;
		padding: 4px 16px !important;

		&:last-child {
			overflow-wrap: break-word;
			word-break: break-word;
		}
	}
</style>
