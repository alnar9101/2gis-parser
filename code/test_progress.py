from progress import load_progress, save_progress


save_progress("164", 2, "in_progress")

print("Рубрика в работе:")
print(load_progress())

save_progress("164", 2, "completed")

print("Рубрика завершена:")
print(load_progress())