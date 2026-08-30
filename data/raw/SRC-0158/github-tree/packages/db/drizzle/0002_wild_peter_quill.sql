CREATE TYPE "public"."quiz_mode" AS ENUM('all', 'unseen', 'wrong');--> statement-breakpoint
CREATE TYPE "public"."quiz_order" AS ENUM('random', 'sequential');--> statement-breakpoint
CREATE TYPE "public"."quiz_session_status" AS ENUM('active', 'completed', 'abandoned');--> statement-breakpoint
CREATE TABLE "quiz_attempts" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"session_id" uuid NOT NULL,
	"user_id" uuid NOT NULL,
	"question_id" uuid NOT NULL,
	"selected_answers" jsonb NOT NULL,
	"correct" boolean NOT NULL,
	"attempted_at" timestamp with time zone DEFAULT now() NOT NULL,
	CONSTRAINT "quiz_attempts_session_question_unique" UNIQUE("session_id","question_id"),
	CONSTRAINT "quiz_attempts_answers_check" CHECK (jsonb_typeof("quiz_attempts"."selected_answers") = 'array' AND jsonb_array_length("quiz_attempts"."selected_answers") > 0)
);
--> statement-breakpoint
CREATE TABLE "quiz_preferences" (
	"user_id" uuid NOT NULL,
	"certification_code" "certification_code" NOT NULL,
	"mode" "quiz_mode" NOT NULL,
	"order" "quiz_order" NOT NULL,
	"question_limit" integer,
	"category_slugs" jsonb NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL,
	CONSTRAINT "quiz_preferences_pk" PRIMARY KEY("user_id","certification_code"),
	CONSTRAINT "quiz_preferences_limit_check" CHECK ("quiz_preferences"."question_limit" IS NULL OR "quiz_preferences"."question_limit" > 0),
	CONSTRAINT "quiz_preferences_categories_check" CHECK (jsonb_typeof("quiz_preferences"."category_slugs") = 'array' AND jsonb_array_length("quiz_preferences"."category_slugs") > 0)
);
--> statement-breakpoint
CREATE TABLE "quiz_queue" (
	"session_id" uuid NOT NULL,
	"position" integer NOT NULL,
	"question_id" uuid NOT NULL,
	CONSTRAINT "quiz_queue_pk" PRIMARY KEY("session_id","position"),
	CONSTRAINT "quiz_queue_session_question_unique" UNIQUE("session_id","question_id"),
	CONSTRAINT "quiz_queue_position_check" CHECK ("quiz_queue"."position" >= 0)
);
--> statement-breakpoint
CREATE TABLE "quiz_sessions" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"user_id" uuid NOT NULL,
	"parent_session_id" uuid,
	"certification_code" "certification_code" NOT NULL,
	"mode" "quiz_mode" NOT NULL,
	"order" "quiz_order" NOT NULL,
	"question_limit" integer,
	"category_slugs" jsonb NOT NULL,
	"status" "quiz_session_status" DEFAULT 'active' NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"completed_at" timestamp with time zone,
	CONSTRAINT "quiz_sessions_id_user_unique" UNIQUE("id","user_id"),
	CONSTRAINT "quiz_sessions_limit_check" CHECK ("quiz_sessions"."question_limit" IS NULL OR "quiz_sessions"."question_limit" > 0),
	CONSTRAINT "quiz_sessions_categories_check" CHECK (jsonb_typeof("quiz_sessions"."category_slugs") = 'array' AND jsonb_array_length("quiz_sessions"."category_slugs") > 0)
);
--> statement-breakpoint
ALTER TABLE "quiz_attempts" ADD CONSTRAINT "quiz_attempts_session_user_fk" FOREIGN KEY ("session_id","user_id") REFERENCES "public"."quiz_sessions"("id","user_id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "quiz_attempts" ADD CONSTRAINT "quiz_attempts_queued_question_fk" FOREIGN KEY ("session_id","question_id") REFERENCES "public"."quiz_queue"("session_id","question_id") ON DELETE restrict ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "quiz_preferences" ADD CONSTRAINT "quiz_preferences_user_id_users_id_fk" FOREIGN KEY ("user_id") REFERENCES "public"."users"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "quiz_queue" ADD CONSTRAINT "quiz_queue_session_id_quiz_sessions_id_fk" FOREIGN KEY ("session_id") REFERENCES "public"."quiz_sessions"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "quiz_queue" ADD CONSTRAINT "quiz_queue_question_id_questions_id_fk" FOREIGN KEY ("question_id") REFERENCES "public"."questions"("id") ON DELETE restrict ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "quiz_sessions" ADD CONSTRAINT "quiz_sessions_user_id_users_id_fk" FOREIGN KEY ("user_id") REFERENCES "public"."users"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "quiz_sessions" ADD CONSTRAINT "quiz_sessions_parent_user_fk" FOREIGN KEY ("parent_session_id","user_id") REFERENCES "public"."quiz_sessions"("id","user_id") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
CREATE INDEX "quiz_attempts_user_attempted_idx" ON "quiz_attempts" USING btree ("user_id","attempted_at");--> statement-breakpoint
CREATE INDEX "quiz_attempts_session_idx" ON "quiz_attempts" USING btree ("session_id","attempted_at");--> statement-breakpoint
CREATE INDEX "quiz_sessions_user_cert_created_idx" ON "quiz_sessions" USING btree ("user_id","certification_code","created_at");--> statement-breakpoint
CREATE FUNCTION reject_quiz_attempt_mutation() RETURNS trigger AS $$
BEGIN
	RAISE EXCEPTION 'quiz attempts are append-only' USING ERRCODE = '55000';
END;
$$ LANGUAGE plpgsql;--> statement-breakpoint
CREATE TRIGGER quiz_attempts_append_only
	BEFORE UPDATE OR DELETE ON "quiz_attempts"
	FOR EACH ROW EXECUTE FUNCTION reject_quiz_attempt_mutation();
