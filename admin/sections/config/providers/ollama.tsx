import { fetchModels } from "@/client/config";
import {
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { toast } from "@/components/ui/use-toast";
import { cn } from "@/lib/utils";
import { useEffect, useState } from "react";
import { UseFormReturn } from "react-hook-form";
import { ModelForm } from "./shared";

const embeddingModels = ["nomic-embed-text"];

const getLLMModels = (models: string[]) => {
  return models.filter((model) => {
    const modelName = model.split(":")[0];
    return !embeddingModels.includes(modelName);
  });
};

const getEmbeddingModels = (models: string[]) => {
  return models.filter((model) => {
    const modelName = model.split(":")[0];
    return embeddingModels.includes(modelName);
  });
};

export const OllamaForm = ({
  form,
  defaultValues,
}: {
  form: UseFormReturn;
  defaultValues: any;
}) => {
  const [models, setModels] = useState<string[]>();
  const [loading, setLoading] = useState(true);

  // Fetch models from the api
  useEffect(() => {
    fetchModels("ollama")
      .then((data) => {
        setModels(data);
      })
      .catch((err) => {
        console.error(err);
        toast({
          className: cn(
            "top-0 right-0 flex fixed md:max-w-[420px] md:top-4 md:right-4 text-red-500",
          ),
          title: "Failed to fetch Ollama models",
          duration: 5000,
        });
      }).finally(() => {
        setLoading(false);
      });
  }, []);

  return (
    <>
      <FormField
        control={form.control}
        name="ollama_base_url"
        render={({ field }) => (
          <FormItem>
            <FormLabel>Ollama Base URL</FormLabel>
            <FormControl>
              <Input
                placeholder={defaultValues.ollama_base_url ?? ""}
                {...field}
              />
            </FormControl>
            <FormDescription>
              Set to http://host.docker.internal:11434 if you are running Ollama
              locally
            </FormDescription>
            <FormMessage />
          </FormItem>
        )}
      />
      {getLLMModels(models ?? []).length === 0 && !loading ? (
        <FormMessage>
          There is no LLM model available using Ollama. <br />
          Please pull a Ollama LLM model from &nbsp;
          <a href="https://ollama.com/library" target="_blank" rel="noreferrer">
            https://ollama.com/library
          </a>
        </FormMessage>
      ) : getEmbeddingModels(models ?? []).length == 0 && !loading ? (
        <>
          <ModelForm
            form={form}
            defaultValues={defaultValues}
            supportedModels={getLLMModels(models ?? [])}
          />
          <FormMessage>
            The embedding model <i>nomic-embed-text</i> is required. Please pull
            it from{" "}
            <a
              href="https://ollama.com/library/nomic-embed-text"
              target="_blank"
              rel="noreferrer"
            >
              {" "}
              https://ollama.com/library/nomic-embed-text
            </a>
          </FormMessage>
        </>
      ) : (
        <ModelForm
          form={form}
          defaultValues={defaultValues}
          supportedModels={getLLMModels(models ?? [])}
        />
      )}
    </>
  );
};
