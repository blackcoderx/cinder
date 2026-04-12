import { defineConfig } from "astro/config";
import starlight from "@astrojs/starlight";

// https://astro.build/config
export default defineConfig({
  integrations: [
    starlight({
      title: "CinderAPI",
      customCss: ["@fontsource/jetbrains-mono", "./src/styles/custom.css"],
      components: {
        SocialIcons: "./src/components/GitHubLink.astro",
      },
      sidebar: [
        {
          label: "Getting Started",
          autogenerate: { directory: "getting-started" },
        },
        {
          label: "Core Concepts",
          collapsed: false,
          items: [
            { label: "The Cinder App", link: "/core-concepts/app/" },
            { label: "Collections", link: "/core-concepts/collections/" },
            { label: "Field Types", link: "/fields/field-types/" },
            { label: "Relations", link: "/core-concepts/relations/" },
            { label: "Access Control", link: "/core-concepts/access-control/" },
            {
              label: "Lifecycle Hooks",
              link: "/core-concepts/lifecycle-hooks/",
            },
            {
              label: "Schema Auto-Sync",
              link: "/core-concepts/schema-autosync/",
            },
            { label: "Realtime", link: "/core-concepts/realtime/" },
          ],
        },
        {
          label: "Configuration",
          autogenerate: { directory: "configuration" },
        },
        {
          label: "Authentication",
          collapsed: false,
          items: [
            { label: "Overview", link: "/authentication/" },
            { label: "Setup", link: "/authentication/setup/" },
            { label: "User Model", link: "/authentication/user-model/" },
            { label: "Endpoints", link: "/authentication/endpoints/" },
            { label: "Hooks", link: "/authentication/hooks/" },
            { label: "Security", link: "/authentication/security/" },
            {
              label: "Troubleshooting",
              link: "/authentication/troubleshooting/",
            },
          ],
        },
        { label: "Database", autogenerate: { directory: "database" } },
        { label: "Fields", autogenerate: { directory: "fields" } },
        { label: "Migrations", autogenerate: { directory: "migrations" } },
        { label: "Hooks", autogenerate: { directory: "hooks" } },
        {
          label: "Realtime",
          autogenerate: { directory: "realtime" },
        },
        { label: "Caching", autogenerate: { directory: "caching" } },
        {
          label: "Rate Limiting",
          autogenerate: { directory: "rate-limiting" },
        },
        { label: "File Storage", autogenerate: { directory: "file-storage" } },
        { label: "Email", autogenerate: { directory: "email" } },
        { label: "Deployment", autogenerate: { directory: "deployment" } },
        { label: "CLI", autogenerate: { directory: "cli" } },
        { label: "API Reference", autogenerate: { directory: "api" } },
      ],
    }),
  ],
});
