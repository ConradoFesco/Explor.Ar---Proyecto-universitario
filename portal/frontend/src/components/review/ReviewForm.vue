<script setup lang="ts">
import { ref, watch, computed } from "vue";
import { useReviewsStore } from "@/stores/reviews";

const props = defineProps<{
  siteId: number;
  existingReview: {
  id: number;
  rating: number;
  content: string;
} | null;

}>();

const emit = defineEmits(["submitted"]);

const reviewsStore = useReviewsStore();

// Campos del formulario
const rating = ref<number>(props.existingReview?.rating ?? 0);
const content = ref<string>(props.existingReview?.content ?? "");

// Label dinámico para editar vs crear
const isEditing = computed(() => !!props.existingReview);

// Si cambia existingReview, actualizar el form
watch(
  () => props.existingReview,
  (newValue) => {
    if (newValue) {
      rating.value = newValue.rating;
      content.value = newValue.content;
    } else {
      rating.value = 0;
      content.value = "";
    }
  }
);

// Submit del formulario
async function handleSubmit() {
  const reviewData = {
    site_id: props.siteId,
    rating: rating.value,
    content: content.value,
  };

  try {
    if (props.existingReview) {
      // Modo editar
      await reviewsStore.updateReview(props.existingReview.id, {
        rating: rating.value,
        content: content.value,
      });
    } else {
      // Modo crear
      await reviewsStore.createReview(reviewData);
    }

    emit("submitted");

    // Reset solo si es nueva reseña:
    if (!props.existingReview) {
      rating.value = 0;
      content.value = "";
    }

  } catch (err) {
    console.error(err);
  }
}
</script>

<template>
  <div class="p-4 border rounded-xl bg-white shadow-md mt-4">

    <h3 class="text-lg font-bold mb-2">
      {{ isEditing ? "Editar reseña" : "Escribir una reseña" }}
    </h3>

    <!-- Rating -->
    <div class="flex gap-2 mb-3">
      <span
        v-for="star in 5"
        :key="star"
        class="cursor-pointer text-2xl select-none"
        :class="star <= rating ? 'text-yellow-500' : 'text-gray-300'"
        @click="rating = star"
      >
        ★
      </span>
    </div>

    <!-- Contenido -->
    <textarea
      v-model="content"
      class="w-full border px-3 py-2 rounded-lg focus:ring outline-none"
      placeholder="Escribí tu reseña..."
      rows="3"
    ></textarea>

    <!-- Botón -->
    <button
      @click="handleSubmit"
      class="mt-3 bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-lg w-full"
    >
      {{ isEditing ? "Guardar cambios" : "Publicar reseña" }}
    </button>

  </div>
</template>
